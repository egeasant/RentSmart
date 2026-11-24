"""
RentSmart — Sistema de Orçamento de Locação com Python e Orientação a Objetos
Cliente: R.M Imóveis
Disciplina: Algorithmic Thinking & Introduction to Object-Oriented Programming
"""

from abc import ABC, abstractmethod
import csv
import os


def formatar_moeda(valor: float) -> str:
    """Formata um valor numérico no padrão monetário brasileiro (R$ 1.234,56)."""
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


class Imovel(ABC):
    """Classe base abstrata que representa um imóvel disponível para locação."""

    def __init__(self, tipo: str, aluguel_base: float, vagas_garagem: int = 0) -> None:
        self.tipo = tipo
        self.aluguel_base = float(aluguel_base)
        self.vagas_garagem = int(vagas_garagem)

    def calcular_adicional_quartos(self) -> float:
        """Retorna o acréscimo referente à quantidade de quartos (padrão: R$ 0,00)."""
        return 0.0

    @abstractmethod
    def calcular_adicional_garagem(self) -> float:
        """Calcula o acréscimo referente às vagas de garagem/estacionamento."""

    def calcular_subtotal(self) -> float:
        """Calcula o valor do aluguel somado aos adicionais antes de descontos."""
        return (
            self.aluguel_base
            + self.calcular_adicional_quartos()
            + self.calcular_adicional_garagem()
        )

    def calcular_desconto(self) -> float:
        """Retorna o valor do desconto comercial aplicável (padrão: R$ 0,00)."""
        return 0.0

    def calcular_aluguel_mensal(self) -> float:
        """Calcula o valor líquido mensal da locação."""
        return self.calcular_subtotal() - self.calcular_desconto()

    def obter_detalhamento(self) -> dict:
        """Retorna um dicionário estruturado com os componentes do aluguel mensal."""
        return {
            "tipo": self.tipo,
            "aluguel_base": self.aluguel_base,
            "adicional_quartos": self.calcular_adicional_quartos(),
            "adicional_garagem": self.calcular_adicional_garagem(),
            "subtotal": self.calcular_subtotal(),
            "desconto": self.calcular_desconto(),
            "aluguel_mensal": self.calcular_aluguel_mensal(),
        }


class Apartamento(Imovel):
    """Representa um apartamento para locação na R.M Imóveis."""

    ALUGUEL_BASE = 700.00
    ADICIONAL_DOIS_QUARTOS = 200.00
    ADICIONAL_GARAGEM = 300.00
    PERCENTUAL_DESCONTO_SEM_CRIANCAS = 0.05

    def __init__(self, quartos: int, possui_vaga: bool, possui_criancas: bool) -> None:
        if quartos not in (1, 2):
            raise ValueError("Apartamentos devem possuir 1 ou 2 quartos.")
        super().__init__(
            tipo="Apartamento",
            aluguel_base=self.ALUGUEL_BASE,
            vagas_garagem=1 if possui_vaga else 0,
        )
        self.quartos = quartos
        self.possui_criancas = possui_criancas

    def calcular_adicional_quartos(self) -> float:
        return self.ADICIONAL_DOIS_QUARTOS if self.quartos == 2 else 0.0

    def calcular_adicional_garagem(self) -> float:
        return self.ADICIONAL_GARAGEM if self.vagas_garagem == 1 else 0.0

    def calcular_desconto(self) -> float:
        if not self.possui_criancas:
            return self.calcular_subtotal() * self.PERCENTUAL_DESCONTO_SEM_CRIANCAS
        return 0.0


class Casa(Imovel):
    """Representa uma casa para locação na R.M Imóveis."""

    ALUGUEL_BASE = 900.00
    ADICIONAL_DOIS_QUARTOS = 250.00
    ADICIONAL_GARAGEM = 300.00

    def __init__(self, quartos: int, possui_vaga: bool) -> None:
        if quartos not in (1, 2):
            raise ValueError("Casas devem possuir 1 ou 2 quartos.")
        super().__init__(
            tipo="Casa",
            aluguel_base=self.ALUGUEL_BASE,
            vagas_garagem=1 if possui_vaga else 0,
        )
        self.quartos = quartos

    def calcular_adicional_quartos(self) -> float:
        return self.ADICIONAL_DOIS_QUARTOS if self.quartos == 2 else 0.0

    def calcular_adicional_garagem(self) -> float:
        return self.ADICIONAL_GARAGEM if self.vagas_garagem == 1 else 0.0


class Estudio(Imovel):
    """Representa um estúdio para locação na R.M Imóveis."""

    ALUGUEL_BASE = 1200.00
    PACOTE_DUAS_VAGAS = 250.00
    VALOR_VAGA_ADICIONAL = 60.00

    def __init__(self, vagas_garagem: int = 0) -> None:
        if vagas_garagem < 0 or vagas_garagem == 1:
            raise ValueError(
                "Para estúdios, informe 0 vagas ou a partir de 2 vagas (pacote inicial)."
            )
        super().__init__(
            tipo="Estúdio",
            aluguel_base=self.ALUGUEL_BASE,
            vagas_garagem=vagas_garagem,
        )

    def calcular_adicional_garagem(self) -> float:
        if self.vagas_garagem == 0:
            return 0.0
        vagas_extras = max(0, self.vagas_garagem - 2)
        return self.PACOTE_DUAS_VAGAS + (vagas_extras * self.VALOR_VAGA_ADICIONAL)


class OrcamentoLocacao:
    """Gerencia o orçamento completo, a taxa contratual e a projeção anual em CSV."""

    TAXA_CONTRATUAL = 2000.00
    MAX_PARCELAS = 5

    def __init__(self, imovel: Imovel, parcelas_taxa: int) -> None:
        if not 1 <= parcelas_taxa <= self.MAX_PARCELAS:
            raise ValueError("A taxa contratual deve ser parcelada entre 1 e 5 vezes.")
        self.imovel = imovel
        self.parcelas_taxa = parcelas_taxa

    def calcular_valor_parcela_taxa(self) -> float:
        """Retorna o valor de cada parcela da taxa contratual."""
        return self.TAXA_CONTRATUAL / self.parcelas_taxa

    def gerar_projecao_anual(self) -> list[dict]:
        """Gera a projeção mês a mês para os primeiros 12 meses de contrato."""
        aluguel_mensal = self.imovel.calcular_aluguel_mensal()
        valor_parcela = self.calcular_valor_parcela_taxa()
        projecao = []

        for mes in range(1, 13):
            parcela_mes = valor_parcela if mes <= self.parcelas_taxa else 0.0
            total_mes = aluguel_mensal + parcela_mes
            status_taxa = (
                f"Parcela {mes}/{self.parcelas_taxa}"
                if mes <= self.parcelas_taxa
                else "Quitada"
            )
            projecao.append(
                {
                    "mes": mes,
                    "aluguel_mensal": round(aluguel_mensal, 2),
                    "parcela_taxa": round(parcela_mes, 2),
                    "total_mes": round(total_mes, 2),
                    "status_taxa": status_taxa,
                }
            )
        return projecao

    def exibir_resumo(self) -> None:
        """Exibe no terminal o resumo detalhado do orçamento e condições contratuais."""
        detalhes = self.imovel.obter_detalhamento()
        valor_parcela = self.calcular_valor_parcela_taxa()
        total_com_parcela = detalhes["aluguel_mensal"] + valor_parcela

        print("\n" + "=" * 62)
        print("           RENTSMART — RESUMO DO ORÇAMENTO DE LOCAÇÃO")
        print("=" * 62)
        print(f"Categoria do Imóvel : {detalhes['tipo']}")

        if isinstance(self.imovel, (Apartamento, Casa)):
            print(f"Configuração        : {self.imovel.quartos} quarto(s)")
        print(f"Vagas de Garagem    : {self.imovel.vagas_garagem} vaga(s)")

        if isinstance(self.imovel, Apartamento):
            criancas_txt = "Sim" if self.imovel.possui_criancas else "Não (elegível a 5% de desconto)"
            print(f"Possui Crianças     : {criancas_txt}")

        print("-" * 62)
        print("1. COMPOSIÇÃO DO ALUGUEL MENSAL (RECORRENTE)")
        print(f"   Aluguel-base                    : {formatar_moeda(detalhes['aluguel_base'])}")
        print(f"   Adicional de quartos            : {formatar_moeda(detalhes['adicional_quartos'])}")
        print(f"   Adicional de garagem/estacion.  : {formatar_moeda(detalhes['adicional_garagem'])}")
        print(f"   Subtotal mensal                 : {formatar_moeda(detalhes['subtotal'])}")
        print(f"   Desconto comercial aplicado     : - {formatar_moeda(detalhes['desconto'])}")
        print(f"   >>> VALOR DO ALUGUEL MENSAL     : {formatar_moeda(detalhes['aluguel_mensal'])}")

        print("-" * 62)
        print("2. TAXA CONTRATUAL (CUSTO DE CONTRATAÇÃO — SEPARADO DO ALUGUEL)")
        print(f"   Valor total da taxa contratual  : {formatar_moeda(self.TAXA_CONTRATUAL)}")
        print(
            f"   Condição escolhida              : {self.parcelas_taxa}x de "
            f"{formatar_moeda(valor_parcela)} (sem juros)"
        )

        print("-" * 62)
        print("3. RESUMO DO FLUXO FINANCEIRO NO 1º ANO")
        print(
            f"   Meses 1 a {self.parcelas_taxa} (Aluguel + Parcela): "
            f"{formatar_moeda(total_com_parcela)} / mês"
        )
        if self.parcelas_taxa < 12:
            print(
                f"   Meses {self.parcelas_taxa + 1} a 12 (Somente Aluguel) : "
                f"{formatar_moeda(detalhes['aluguel_mensal'])} / mês"
            )
        print("=" * 62)

    def exportar_csv(self, nome_arquivo: str = "orcamento_rentsmart_12_meses.csv") -> str:
        """Exporta a projeção de 12 meses para um arquivo CSV compatível com Excel."""
        projecao = self.gerar_projecao_anual()
        caminho_completo = os.path.abspath(nome_arquivo)

        with open(caminho_completo, mode="w", newline="", encoding="utf-8-sig") as arquivo:
            escritor = csv.writer(arquivo, delimiter=";")
            escritor.writerow(
                [
                    "Mes",
                    "Tipo_Imovel",
                    "Aluguel_Mensal_R$",
                    "Parcela_Taxa_Contratual_R$",
                    "Total_Previsto_Mes_R$",
                    "Status_Taxa_Contratual",
                ]
            )
            for item in projecao:
                escritor.writerow(
                    [
                        f"Mês {item['mes']:02d}",
                        self.imovel.tipo,
                        f"{item['aluguel_mensal']:.2f}".replace(".", ","),
                        f"{item['parcela_taxa']:.2f}".replace(".", ","),
                        f"{item['total_mes']:.2f}".replace(".", ","),
                        item["status_taxa"],
                    ]
                )
        return caminho_completo


class SistemaRentSmart:
    """Controla a interface de linha de comando e a validação das entradas do usuário."""

    @staticmethod
    def ler_opcao(mensagem: str, opcoes_validas: tuple[str, ...]) -> str:
        while True:
            entrada = input(mensagem).strip()
            if entrada in opcoes_validas:
                return entrada
            print(f"[Erro] Opção inválida. Escolha entre: {', '.join(opcoes_validas)}.")

    @staticmethod
    def ler_inteiro(mensagem: str, minimo: int, maximo: int | None = None) -> int:
        while True:
            entrada = input(mensagem).strip()
            try:
                valor = int(entrada)
                if valor < minimo:
                    print(f"[Erro] O valor deve ser maior ou igual a {minimo}.")
                    continue
                if maximo is not None and valor > maximo:
                    print(f"[Erro] O valor deve estar entre {minimo} e {maximo}.")
                    continue
                return valor
            except ValueError:
                print("[Erro] Digite um número inteiro válido.")

    @staticmethod
    def ler_sim_nao(mensagem: str) -> bool:
        while True:
            entrada = input(mensagem).strip().upper()
            if entrada in ("S", "SIM"):
                return True
            if entrada in ("N", "NAO", "NÃO"):
                return False
            print("[Erro] Responda apenas com S (Sim) ou N (Não).")

    def coletar_dados_imovel(self) -> Imovel:
        print("\nSelecione a categoria do imóvel desejado:")
        print("  [1] Apartamento (Base: R$ 700,00)")
        print("  [2] Casa        (Base: R$ 900,00)")
        print("  [3] Estúdio     (Base: R$ 1.200,00)")
        categoria = self.ler_opcao("Digite a opção (1, 2 ou 3): ", ("1", "2", "3"))

        if categoria == "1":
            quartos = self.ler_inteiro(
                "Quantidade de quartos (1 ou 2 — 2 quartos adicionam R$ 200,00): ",
                minimo=1,
                maximo=2,
            )
            possui_vaga = self.ler_sim_nao(
                "Deseja incluir 1 vaga de garagem (+ R$ 300,00/mês)? (S/N): "
            )
            possui_criancas = self.ler_sim_nao(
                "Algum morador possui crianças? (Sem crianças garante 5% de desconto) (S/N): "
            )
            return Apartamento(
                quartos=quartos,
                possui_vaga=possui_vaga,
                possui_criancas=possui_criancas,
            )

        if categoria == "2":
            quartos = self.ler_inteiro(
                "Quantidade de quartos (1 ou 2 — 2 quartos adicionam R$ 250,00): ",
                minimo=1,
                maximo=2,
            )
            possui_vaga = self.ler_sim_nao(
                "Deseja incluir 1 vaga de garagem (+ R$ 300,00/mês)? (S/N): "
            )
            return Casa(quartos=quartos, possui_vaga=possui_vaga)

        # Categoria == "3" (Estúdio)
        deseja_estacionamento = self.ler_sim_nao(
            "Deseja contratar o pacote inicial de 2 vagas de estacionamento (R$ 250,00/mês)? (S/N): "
        )
        if not deseja_estacionamento:
            return Estudio(vagas_garagem=0)

        vagas_adicionais = self.ler_inteiro(
            "Quantas vagas adicionais além das 2 iniciais deseja incluir (R$ 60,00/cada)? (0 ou mais): ",
            minimo=0,
        )
        return Estudio(vagas_garagem=2 + vagas_adicionais)

    def executar(self) -> None:
        print("=" * 62)
        print("     BEM-VINDO AO RENTSMART — R.M IMÓVEIS")
        print("     Sistema Automatizado de Orçamento de Locação")
        print("=" * 62)

        imovel = self.coletar_dados_imovel()
        parcelas = self.ler_inteiro(
            "\nEm quantas parcelas deseja pagar a taxa contratual de R$ 2.000,00 (1 a 5)? ",
            minimo=1,
            maximo=5,
        )

        orcamento = OrcamentoLocacao(imovel=imovel, parcelas_taxa=parcelas)
        orcamento.exibir_resumo()

        caminho_csv = orcamento.exportar_csv()
        print(f"\n[Sucesso] Projeção de 12 meses exportada para:\n{caminho_csv}\n")


if __name__ == "__main__":
    app = SistemaRentSmart()
    app.executar()