#!/usr/bin/env python
# coding: utf-8

# In[7]:


#Importando as bibliotecas necessárias para a condução do projeto
import pandas as pd
import zipfile
import io
import requests
import os
import csv
from pathlib import Path
from tkinter import *
import tkinter.filedialog
from tkinter import messagebox
import tkinter as tk

# URL do arquivo ZIP contido no site
url = 'http://repositorio.dados.gov.br/seplan/PPA2016-2019.zip'

#interface- Abrindo janela para seleção do usuário
janela = Tk()

#usuário seleciona o diretório que deseja salvar os arquivos
salvar_arquivo = tkinter.filedialog.askdirectory(title = 'Selecione o caminho onde o arquivo será armazenado')
salvar_arquivo1 = Path(salvar_arquivo)

#alerta pora informar o usuário que o programa está em andamento
messagebox.showinfo('Status do Programa', 'Programa em andamento, aguarde!')
janela.destroy()

#escolhendo um nome para o arquivo
nome_arquivo1 = 'Base_Geral.xlsx'

#especificando o caminho completo
local_armazenamento = salvar_arquivo1 / Path('{}/{}'.format(salvar_arquivo,nome_arquivo1))

#definindo diretório para salvar o arquivo
diretorio_salvar = salvar_arquivo

# Função para listar arquivos CSV dentro do ZIP
def listar_arquivos_zip(z):
    #listar os nomes dos arquivos
    zip_files = z.namelist()
    #transformando os nomes dos arquivos em letras minúscula e selecionando somente os arquivos que terminam com extensão .csv
    csv_files = [file_name for file_name in zip_files if file_name.lower().endswith('.csv')]
    #como resultado da função, retornar o nome do csv
    return csv_files

# Função para carregar tabela a partir do arquivo ZIP com múltiplos separadores
def carregar_tabela(file_name, z, sep_patterns):
    try:
        # Ler o arquivo CSV diretamente do ZIP, separando por múltiplos delimitadores
        with z.open(file_name) as file:
            # Carregar o conteúdo do CSV em um DataFrame pandas
            # Verificar e substituir as aspas duplas nos dados do DataFrame
            df = pd.read_csv(file, sep=sep_patterns, quotechar='"', error_bad_lines=False, warn_bad_lines=True)
            
                
            return df
    #definindo exceções e realizando o print dos csv que deram erros
    except pd.errors.ParserError as e:
        print(f'Erro ao processar CSV {file_name}: {e}')
        return None
    except Exception as e:
        print(f'Erro desconhecido ao processar CSV {file_name}: {e}')
        return None

# Fazer a requisição GET para baixar o arquivo ZIP
response = requests.get(url)

# Verificar se a requisição foi bem-sucedida
if response.status_code == 200:
    # Extrair o conteúdo do arquivo ZIP
    z = zipfile.ZipFile(io.BytesIO(response.content))
    
    # Listar os arquivos CSV dentro do ZIP
    arquivos_csv = listar_arquivos_zip(z)
    print(f'Arquivos CSV disponíveis: {arquivos_csv}')
    
    # Criar um dicionário para armazenar os DataFrames de cada tabela
    tabelas = {}
    
    # Iterar sobre cada arquivo CSV encontrado
    for idx, arquivo_csv in enumerate(arquivos_csv):
        # Nome da variável para cada tabela (Tabela1, Tabela2, etc.)
        nome_variavel = f'Tabela{idx + 1}'
        
        # Carregar o DataFrame do arquivo CSV, separando por ';' e '|'
        df = carregar_tabela(arquivo_csv, z, sep_patterns='[;|]')
        
        if df is not None:
            tabelas[nome_variavel] = df
            print(f'Tabela carregada com sucesso: {nome_variavel} ({arquivo_csv})')
            print(f'Número de linhas: {df.shape[0]}')
            print(f'Número de colunas: {df.shape[1]}')
            print('Colunas:')
            # Lista todas as colunas do DataFrame
            display(df.columns.tolist())  
            print('\n')
            
            # Salvar o DataFrame como arquivo CSV no diretório especificado
            nome_arquivo_csv = os.path.join(diretorio_salvar, f'{nome_variavel}.csv')
            # Index=False para não incluir o índice no CSV
            df.to_csv(nome_arquivo_csv, index=False)  
            
        else:
            print(f'Erro ao carregar tabela: {arquivo_csv}')
    
    # Exemplo de acesso a uma tabela específica
    if 'Tabela1' in tabelas:
        print('Exemplo de acesso à Tabela1:')
        display(tabelas['Tabela3'].head())

else:
    print(f'Erro na requisição: {response.status_code}')


# In[8]:


# Função para substituir " por nada em todas as tabelas
def substituir_aspas(tabelas):
    for chave, df in tabelas.items():
        # Substituir aspas nos nomes das colunas
        df.columns = df.columns.str.replace('"', '')

        # Substituir aspas nos dados das colunas
        for coluna in df.columns:
            if df[coluna].dtype == 'object':
                df[coluna] = df[coluna].str.replace('"', '')

        tabelas[chave] = df
    return tabelas

# Função para deixar todas as strings nas células do DataFrame em caixa alta
def deixar_caixa_alta(df_dict):
    for key, df in df_dict.items():  # Itera sobre cada DataFrame no dicionário
        for col in df.columns:
            if df[col].dtype == 'object':  # Verifica se a coluna contém strings
                df[col] = df[col].str.upper()  # Converte todas as strings para caixa alta
        df_dict[key] = df  # Atualiza o DataFrame no dicionário

    return df_dict

# Chamar a função para substituir aspas em todas as tabelas carregadas
tabelas = substituir_aspas(tabelas)
tabelas = deixar_caixa_alta(tabelas)


# # Concatenando as tabelas com dados complementares

# In[9]:


#Concat nas tabelas com os mesmos conjuntos de dados e ignorando index
iniciativas1 = pd.concat([tabelas['Tabela1'], tabelas['Tabela2'], tabelas['Tabela3']], ignore_index=True)
iniciativas2 = pd.concat([tabelas['Tabela7'], tabelas['Tabela8'], tabelas['Tabela9']], ignore_index=True)
#-------------------------------------------------------------------------------------------------------------
ind_ref = pd.concat([tabelas['Tabela4'], tabelas['Tabela5'], tabelas['Tabela6']], ignore_index=True)
#-------------------------------------------------------------------------------------------------------------
programas = pd.concat([tabelas['Tabela10'], tabelas['Tabela11'], tabelas['Tabela12']], ignore_index=True)
#-------------------------------------------------------------------------------------------------------------
orgao1 = pd.concat([tabelas['Tabela13'], tabelas['Tabela14'], tabelas['Tabela15']], ignore_index=True)
orgao2 = pd.concat([tabelas['Tabela16'], tabelas['Tabela17'], tabelas['Tabela18']], ignore_index=True)
#-------------------------------------------------------------------------------------------------------------
completa = pd.concat([tabelas['Tabela19'], tabelas['Tabela20'], tabelas['Tabela21']], ignore_index=True)


# # Trabalhando as iniciativas das tabelas 1 a 3 e 7 a 9

# In[45]:


#Realizando o merge das duas bases semelhantes
cons_iniciativas = iniciativas2.merge(iniciativas1[['Iniciativa', 'Anexo PPA', 'Data início', 'Data término', 'Custo total']], on='Iniciativa', how='left')


# In[46]:


#concatenando as iniciativas em uma só base
cons_iniciativas = pd.concat([iniciativas1, iniciativas2], ignore_index=True)


#removendo possíveis duplicatas de acordos com as colunas "especificado como após "subset" abaixo
cons_iniciativas.drop_duplicates(subset=['Exercício', 'Iniciativa', 'Título da Iniciativa'], keep='first')

def convert_padrao_data(date_str):
    try:
        return pd.to_datetime(date_str, format='%d.%m.%Y')
    except ValueError:
        # Verifica se a data está no formato YYYY-MM-DD e converte para dd.mm.aaaa
        if '-' in date_str:
            try:
                return pd.to_datetime(date_str).strftime('%d.%m.%Y')
            except ValueError:
                return pd.NaT  # Retorna NaT se não puder converter
        else:
            return pd.NaT

# Aplicando a função convert_padrao_data às colunas 'Data início' e 'Data término'
cons_iniciativas['Data início'] = cons_iniciativas['Data início'].apply(convert_padrao_data)
cons_iniciativas['Data término'] = cons_iniciativas['Data término'].apply(convert_padrao_data)

# Função para formatar valor monetário no formato brasileiro
def formatar_valor(valor):
    return '{:,.2f}'.format(valor).replace('.', ' ').replace(',', '.').replace(' ', ',')

# Aplicando a formatação à coluna 'Custo total'
cons_iniciativas['Custo total'] = cons_iniciativas['Custo total'].apply(formatar_valor)

#Contar a quantidade de iniciativas e dar um display na tabela
qtd_iniciativas = cons_iniciativas['Título da Iniciativa'].nunique()
print(f'Temos um total de: {qtd_iniciativas} iniciativas distintas nos anos de 2016 a 2018')
display(cons_iniciativas)


# # Trabalhando os programas das tabelas 10 a 12 ; 13 a 15; 4 a 6 e 16 a 18

# In[47]:


#Realizando o merge das duas bases semelhantes
prog_orgao = programas.merge(orgao2[['Programa', 'Órgão']], on='Programa', how='inner')

#removendo possíveis duplicatas
prog_orgao.drop_duplicates(subset=['Exercício', 'Programa', 'Objetivo', 'Meta'], keep='first', inplace=True)

#Renomeando a coluna do df
prog_orgao = prog_orgao.rename(columns={'Descrição_Orgão': 'Descrição Orgão'})


# In[48]:


orgao1 = orgao1.merge(prog_orgao[['Programa', 'Título do Programa', 'Enunciado do Objetivo', 'Órgão']], on='Programa', how='left')

#removendo possíveis duplicatas
orgao1.drop_duplicates(subset=['Exercício', 'Programa', 'Objetivo', 'Meta'], keep='first', inplace=True)


# In[49]:


orgao1 = orgao1.merge(ind_ref[['Programa', 'Descrição do Indicador', 'Unidade de Medida', 'Índice de Referência', 'Data de Apuração']], on='Programa', how='inner')


# In[50]:


orgao1 = orgao1.merge(completa[['Programa', 'Valor Individualização Fiscal Seguridade',
 'Valor Individualização Investimento',
 'Valor Individualização Outras Fontes',
 'Despesas Correntes Ano1',
 'Despesas Capital Ano1',
 'Orçamento Investimento Empresas Estatais Ano1',
 'Crédito e Demais Fontes Ano1',
 'Gasto Tributário Ano1',
 'Despesas Correntes Ano2',
 'Despesas Capital Ano2',
 'Orçamento Investimento Empresas Estatais Ano2',
 'Crédito e Demais Fontes Ano2',
 'Gasto Tributário Ano2',
 'Despesas Correntes Ano3',
 'Despesas Capital Ano3',
 'Orçamento Investimento Empresas Estatais Ano3',
 'Crédito e Demais Fontes Ano3',
 'Gasto Tributário Ano3',
 'Despesas Correntes Ano4',
 'Despesas Capital Ano4',
 'Orçamento Investimento Empresas Estatais Ano4',
 'Crédito e Demais Fontes Ano4',
 'Gasto Tributário Ano4',
 'Despesas Correntes Anos Faltantes',
 'Despesas Capital Anos Faltantes',
 'Orçamento Investimento Empresas Estatais Anos Faltantes',
 'Crédito e Demais Fontes Anos Faltantes',
 'Gasto Tributário Anos Faltantes']], on='Programa', how='left')


# In[51]:


#removendo possíveis duplicatas
orgao1.drop_duplicates(subset=['Exercício', 'Programa', 'Objetivo', 'Meta', 'Valor Regionalizado'], keep='first', inplace=True)


# In[52]:


# Preenchendo os valores NaN com "Não definido"
orgao1['Região'].fillna('Não definido', inplace=True)
orgao1['Unidade de Medida da Meta Regionalizada'].fillna('Não definido', inplace=True)


# In[53]:


qtd_iniciativas = orgao1['Título do Programa'].nunique()
print(f'Temos um total de: {qtd_iniciativas} programas distintos nos anos de 2016 a 2018')


# # UNINDO E TRABALHANDO COM SOMENTE UMA TABELA

# In[54]:


# Criando a coluna 'Junção' com a junção das colunas 'Programa' e 'Objetivo'
cons_iniciativas['Junção'] = cons_iniciativas.apply(lambda row: f"{row['Programa']} - {row['Objetivo']}", axis=1)

# Criando a coluna 'Junção' com a junção das colunas 'Programa' e 'Objetivo'
orgao1['Junção'] = orgao1.apply(lambda row: f"{row['Programa']} - {row['Objetivo']}", axis=1)


# In[55]:


#Mesclando as tabelas com bases na coluna junção criada
total_geral = cons_iniciativas.merge(orgao1[['Meta',
 'Descrição da Meta',
 'Descrição Orgão',
 'Região',
 'Valor Regionalizado',
 'Unidade de Medida da Meta Regionalizada',
 'Título do Programa',
 'Enunciado do Objetivo',
 'Órgão',
 'Descrição do Indicador',
 'Unidade de Medida',
 'Índice de Referência',
 'Data de Apuração',
 'Valor Individualização Fiscal Seguridade',
 'Valor Individualização Investimento',
 'Valor Individualização Outras Fontes',
 'Despesas Correntes Ano1',
 'Despesas Capital Ano1',
 'Orçamento Investimento Empresas Estatais Ano1',
 'Crédito e Demais Fontes Ano1',
 'Gasto Tributário Ano1',
 'Despesas Correntes Ano2',
 'Despesas Capital Ano2',
 'Orçamento Investimento Empresas Estatais Ano2',
 'Crédito e Demais Fontes Ano2',
 'Gasto Tributário Ano2',
 'Despesas Correntes Ano3',
 'Despesas Capital Ano3',
 'Orçamento Investimento Empresas Estatais Ano3',
 'Crédito e Demais Fontes Ano3',
 'Gasto Tributário Ano3',
 'Despesas Correntes Ano4',
 'Despesas Capital Ano4',
 'Orçamento Investimento Empresas Estatais Ano4',
 'Crédito e Demais Fontes Ano4',
 'Gasto Tributário Ano4',
 'Despesas Correntes Anos Faltantes',
 'Despesas Capital Anos Faltantes',
 'Orçamento Investimento Empresas Estatais Anos Faltantes',
 'Crédito e Demais Fontes Anos Faltantes',
 'Gasto Tributário Anos Faltantes',
 'Junção']], on='Junção', how='left')


# In[56]:


#salvando um df final
total_geral.to_excel(local_armazenamento, index=False)


# In[57]:


#mensagem final para o usuário
janela = Tk()
messagebox.showinfo('Status do Programa', 'Programa concluído com sucesso!')
janela.destroy()


# In[ ]:




