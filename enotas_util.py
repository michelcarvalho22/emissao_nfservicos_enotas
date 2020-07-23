import requests
import json
from django.conf import settings
from datetime import date, timedelta, datetime
from  bs4 import BeautifulSoup
from nilusnfs.models import Paramnfs,ErrosParametrosNFS,NotasFiscais
from nilusadm.models import Sequenciais

def cad_empresa_emissora(paramnfs):

        url = settings.ENOTASURL +'/empresas'

        if paramnfs.simples_nac:
            simples = 'true'
        else:
            simples = 'false'

        if paramnfs.incent_cult:
            incentivo = 'true'
        else:
            incentivo = 'false'

        data = {
            "id": str(paramnfs.key_empresa),
            "status": "Habilitada",
            "prazo": 0,
            "dadosObrigatoriosPreenchidos": "true",
            "cnpj": paramnfs.company.cnpj_cpf,
            "inscricaoMunicipal": paramnfs.company.insc_mun,
            "inscricaoEstadual": paramnfs.company.insc_est,
            "razaoSocial": paramnfs.company.razao,
            "nomeFantasia": paramnfs.company.fantasia,
            "optanteSimplesNacional": simples,
            "email": paramnfs.company.email,
            "telefoneComercial": paramnfs.company.telefone,
            "endereco": {
                "pais": "Brasil",
                "codigoIbgeUf": paramnfs.company.ibge_uf,
                "codigoIbgeCidade": paramnfs.company.ibge_mun,
                "uf": paramnfs.company.uf,
                "cidade": paramnfs.company.cidade,
                "logradouro": paramnfs.company.endereco,
                "numero": paramnfs.company.numero,
                "complemento": paramnfs.company.complemento,
                "bairro": paramnfs.company.bairro,
                "cep": paramnfs.company.cep
            },
            "incentivadorCultural": incentivo,
            "regimeEspecialTributacao": paramnfs.regime_trib,
            "ConfiguracoesNFSeProducao": {
                "sequencialNFe": paramnfs.conf_sequenciaNFE,
                "serieNFe": paramnfs.conf_serieNFE,
                "sequencialLoteNFe": paramnfs.conf_sequencialoteNFe,
                "usuarioAcessoProvedor": paramnfs.conf_usuarioAcesso,
                "senhaAcessoProvedor": paramnfs.conf_senhaUsuarioAcesso,
            },
            "codigoServicoMunicipal": paramnfs.cd_srv_padrao,
            "itemListaServicoLC116": paramnfs.it_lista_srv,
            "cnae": paramnfs.cnae,
            "aliquotaIss": str(paramnfs.aliquota_iss),
            "descricaoServico": paramnfs.desc_srv,
            "enviarEmailCliente": "true"
        }

        resposta = requests.post(
            url,json=data,headers={"Authorization": "Basic"+settings.ENOTASKEY}
        )



        xml = BeautifulSoup(resposta.text,"lxml")


        if resposta.status_code == 200:
            key_emp = xml.find("empresaid").contents[0]
            paramnfs.key_empresa = key_emp
            paramnfs.save()
        if resposta.status_code == 400:
            erromsg = xml.find("mensagem").contents[0]
            erro = ErrosParametrosNFS()
            erro.master_user = paramnfs.master_user
            erro.paramnfs = paramnfs
            erro.mensagem = erromsg
            erro.save()


def edit_empresa_emissora(paramnfs):
    url = settings.ENOTASURL + '/empresas'

    if paramnfs.simples_nac:
        simples = 'true'
    else:
        simples = 'false'

    if paramnfs.incent_cult:
        incentivo = 'true'
    else:
        incentivo = 'false'

    data = {
        "id": str(paramnfs.key_empresa),
        "status": "Habilitada",
        "prazo": 0,
        "dadosObrigatoriosPreenchidos": "true",
        "cnpj": paramnfs.company.cnpj_cpf,
        "inscricaoMunicipal": paramnfs.company.insc_mun,
        "inscricaoEstadual": paramnfs.company.insc_est,
        "razaoSocial": paramnfs.company.razao,
        "nomeFantasia": paramnfs.company.fantasia,
        "optanteSimplesNacional": simples,
        "email": paramnfs.company.email,
        "telefoneComercial": paramnfs.company.telefone,
        "endereco": {
            "pais": "Brasil",
            "codigoIbgeUf": paramnfs.company.ibge_uf,
            "codigoIbgeCidade": paramnfs.company.ibge_mun,
            "uf": paramnfs.company.uf,
            "cidade": paramnfs.company.cidade,
            "logradouro": paramnfs.company.endereco,
            "numero": paramnfs.company.numero,
            "complemento": paramnfs.company.complemento,
            "bairro": paramnfs.company.bairro,
            "cep": paramnfs.company.cep
        },
        "incentivadorCultural": incentivo,
        "regimeEspecialTributacao": paramnfs.regime_trib,
        "ConfiguracoesNFSeProducao": {
            "sequencialNFe": paramnfs.conf_sequenciaNFE,
            "serieNFe": paramnfs.conf_serieNFE,
            "sequencialLoteNFe": paramnfs.conf_sequencialoteNFe,
            "usuarioAcessoProvedor": paramnfs.conf_usuarioAcesso,
            "senhaAcessoProvedor": paramnfs.conf_senhaUsuarioAcesso,
        },
        "codigoServicoMunicipal": paramnfs.cd_srv_padrao,
        "itemListaServicoLC116": paramnfs.it_lista_srv,
        "cnae": paramnfs.cnae,
        "aliquotaIss": str(paramnfs.aliquota_iss),
        "descricaoServico": paramnfs.desc_srv,
        "enviarEmailCliente": "true"
    }

    resposta = requests.post(
        url, json=data, headers={"Authorization": "Basic "+settings.ENOTASKEY}
    )



    xml = BeautifulSoup(resposta.text, "lxml")

    if resposta.status_code != 200:
        erromsg = xml.find("mensagem").contents[0]
        erro = ErrosParametrosNFS()
        erro.master_user = paramnfs.master_user
        erro.paramnfs = paramnfs
        erro.mensagem = erromsg
        erro.save()



def emite_nfse(servico):

        seq = Sequenciais.objects.get(user=servico.master_user)
        seq.seq_fatura = seq.seq_fatura + 1
        seq.save()

        data_emissao = datetime.today

        paramnfs = Paramnfs.objects.get(company=servico.company)
        url = settings.ENOTASURL + '/empresas/' + paramnfs.key_empresa + '/nfes'

        if servico.tipo == 'C':
            id_externo = servico.tipo + str(servico.contrato.pk) + str(seq.seq_fatura) + str(
                paramnfs.master_user.pk)
            valor_nota = servico.vlr_fat

        elif servico.tipo == 'O':
            id_externo = servico.tipo + str(servico.os.pk) + str(seq.seq_fatura) + str(
                paramnfs.master_user.pk)
            valor_nota = servico.vlr_fat
        elif servico.tipo == 'N':
            id_externo = servico.pk
            valor_nota = servico.vlr_nota

        cnpj_cpf = servico.cadgeral.cnpj_cpf.replace('.', '')
        cnpj_cpf = cnpj_cpf.replace('-', '')
        cnpj_cpf = cnpj_cpf.replace('/', '')

        if len(cnpj_cpf) < 12:
            tp_pessoa = 'F'
        else:
            tp_pessoa = 'J'

        data = {'cliente':
                    {'tipoPessoa': tp_pessoa,
                     'nome': servico.cadgeral.razao,
                     'email': servico.cadgeral.email,
                     'cpfCnpj': servico.cadgeral.cnpj_cpf,
                     'inscricaoMunicipal': None,
                     'inscricaoEstadual': None,
                     'telefone': servico.cadgeral.telefone,
                     'endereco':
                         {'pais': 'Brasil',
                          'uf': servico.cadgeral.uf,
                          'cidade': servico.cadgeral.cidade,
                          'logradouro': servico.cadgeral.endereco,
                          'numero': servico.cadgeral.numero,
                          'complemento': servico.cadgeral.complemento,
                          'bairro': servico.cadgeral.bairro,
                          'cep': servico.cadgeral.cep
                          },
                     },
                'enviarPorEmail': paramnfs.conf_enviaEmail,
                'id': None,
                'ambienteEmissao': 'Producao',
                'tipo': 'NFS-e',
                'idExterno': id_externo ,
                'consumidorFinal': True,
                'indicadorPresencaConsumidor': None,
                'servico':
                    {'descricao': paramnfs.desc_srv,
                     'aliquotaIss': float(paramnfs.aliquota_iss),
                     'issRetidoFonte': False,
                     'cnae': None,
                     'codigoServicoMunicipio': paramnfs.cd_srv_padrao,
                     'descricaoServicoMunicipio': paramnfs.desc_srv,
                     'itemListaServicoLC116': paramnfs.it_lista_srv,
                     'ufPrestacaoServico': paramnfs.company.uf,
                     'municipioPrestacaoServico': paramnfs.company.uf,
                     'valorCofins': 0,
                     'valorCsll': 0,
                     'valorInss': 0,
                     'valorIr': 0,
                     'valorPis': 0,
                     'observacoes': ''
                     },
                'valorTotal': float(valor_nota),
                'idExternoSubstituir': None,
                'nfeIdSubstitituir': None
                }



        resposta = requests.post(
            url, json=data, headers={"Authorization": "Basic "+settings.ENOTASKEY}
        )
        # print(resposta)
        # print(resposta.text)
        # print(data)

        if resposta.status_code == 200:
            xml = BeautifulSoup(resposta.text, "lxml")

            key_nfs = xml.find("nfeid").contents[0]

            url = url+'/'+key_nfs

            retorno_emissao = requests.get(
                url,  headers={"Authorization": "Basic " + settings.ENOTASKEY}
            )

            # print(retorno_emissao)
            # print(retorno_emissao.text)

            xmlret = BeautifulSoup(retorno_emissao.text,"lxml")
            statusret = xmlret.find("status").contents[0]




            nfs = NotasFiscais()
            nfs.master_user = servico.master_user
            nfs.company = servico.company
            nfs.cadgeral = servico.cadgeral
            nfs.id_key = key_nfs
            nfs.vlr_nota = valor_nota
            data_emissao = xmlret.find("datacriacao").contents[0]
            nfs.data_emissao = datetime.strptime(data_emissao,"%Y-%m-%dT%H:%M:%SZ")
            nfs.desc_status_nfs = statusret
            nfs.envio_concluido = 'N'
            nfs.id_origem = id_externo
            if servico.tipo != 'N':
                nfs.tipo_origem = servico.tipo
            nfs.tipo = 'N'
            if statusret == 'Autorizada':
                num_nf = xmlret.find("nfe").contents[9]
                nfs.num_nf = num_nf.text
                nfs.link_pdf = xmlret.find("linkdownloadpdf").contents[0]
                nfs.link_xml = xmlret.find("linkdownloadxml").contents[0]
            elif statusret == 'Negada':
                nfs.motivoStatus = xmlret.find("motivostatus").contents[0]
            nfs.save()

            return resposta



def refresh_situacao_nfs(nfs):

   for nf in nfs:
        paramnfs = Paramnfs.objects.get(company=nf.company)
        url = settings.ENOTASURL + '/empresas/' + paramnfs.key_empresa + '/nfes/'+nf.id_key

        retorno_nota_fiscal = requests.get(
               url,  headers={"Authorization": "Basic " + settings.ENOTASKEY}
        )
        xmlret = BeautifulSoup(retorno_nota_fiscal.text, "lxml")
        statusret = xmlret.find("status").contents[0]
        if statusret == 'Autorizada':
                num_nf = xmlret.find("nfe").contents[9]
                link_pdf = xmlret.find("linkdownloadpdf").contents[0]
                link_xml = xmlret.find("linkdownloadxml").contents[0]
                data_nota = xmlret.find("dataautorizacao").contents[0]
                data_nota = datetime.strptime(data_nota,"%Y-%m-%dT%H:%M:%SZ")



        elif statusret == 'Negada':
            motivoStatus = xmlret.find("motivostatus").contents[0]


        nota_fiscal = NotasFiscais.objects.get(pk=nf.pk,master_user=nf.master_user)
        nota_fiscal.desc_status_nfs = statusret
        if statusret == 'Autorizada':
            nota_fiscal.num_nf = num_nf.text
            nota_fiscal.link_pdf = link_pdf
            nota_fiscal.link_xml = link_xml
            nota_fiscal.data_emissao = data_nota
            nfs.envio_concluido = 'S'
        elif statusret == 'Negada':
            nota_fiscal.motivoStatus = motivoStatus
            nota_fiscal.envio_concluido = 'S'
        elif statusret == 'Cancelada':
            nota_fiscal.envio_concluido = 'S'
        nota_fiscal.save()

        # emite_nfse(nf)

def consulta_nfs(nf):
    paramnfs = Paramnfs.objects.get(company=nf.company)
    url = settings.ENOTASURL + '/empresas/' + paramnfs.key_empresa + '/nfes/' + nf.id_key

    retorno_nota_fiscal = requests.get(
        url, headers={"Authorization": "Basic " + settings.ENOTASKEY}
    )
    retorno_consulta = BeautifulSoup(retorno_nota_fiscal.text, "lxml")

    return retorno_consulta


def cancela_nfs(nf):


    paramnfs = Paramnfs.objects.get(company=nf.company)
    url = settings.ENOTASURL + '/empresas/' + paramnfs.key_empresa + '/nfes/' + nf.id_key

    requests.delete(
        url, headers={"Authorization": "Basic " + settings.ENOTASKEY}
    )
    retorno_cancelamento = consulta_nfs(nf)

    statusret = retorno_cancelamento.find("status").contents[0]

    nf.desc_status_nfs = statusret
    nf.envio_concluido = 'N'

    if statusret != 'Cancelada':
        motivo_status = retorno_cancelamento.find("motivostatus")
        if motivo_status != None:
            motivoStatus = retorno_cancelamento.find("motivostatus").contents[0]
            nf.motivoStatus = motivoStatus

    nf.save()



