from customtkinter import *
from PIL import Image
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tkinter import ttk
from tkinter import messagebox


conn = sqlite3.connect('clientes.db')
cur = conn.cursor()
conn.commit()

cur.execute('''
CREATE TABLE IF NOT EXISTS clientes (
    nome TEXT,
    valor INT,
    juros INT,
    total INT,
    data TO_DATE,
    entrega TO_DATE
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS fluxo_de_caixa (
    data TO_DATE,
    entrada INT,
    saida INT,
    saldo INT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS parcelados_cartoes (
    nome TEXT,
    valor INT,
    lucro INT,
    total INT,
    qnt_par INT,
    vl_par INT,
    data TO_DATE,
   termino TO_DATE
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS "custo_pessoais" (
    Categoria TEXT,
    Janeiro REAL DEFAULT 0,
    Fevereiro REAL DEFAULT 0,
    Março REAL DEFAULT 0,
    Abril REAL DEFAULT 0,
    Maio REAL DEFAULT 0,
    Junho REAL DEFAULT 0,
    Julho REAL DEFAULT 0,
    Agosto REAL DEFAULT 0,
    Setembro REAL DEFAULT 0,
    Outubro REAL DEFAULT 0,
    Novembro REAL DEFAULT 0,
    Dezembro REAL DEFAULT 0
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS investimentos_pessoais (
    instituicao TEXT,
    valor INT,
    juros INT,
    total INT,
    data TO_DATE
    
)
''')

categorias = [
    'Salários', 
    'Investimentos',
    'Seguro do Carro',
    'Supermercado',
    'Internet',
    'FGTS',
    'Luz',
    'Dieta',
    'Gás',
    'Cabelo',
    'Combustivel de Carro',
    'Manutenção do carro',
    'IPVA',
    'Medico',
    'Outros'
]

for categoria in categorias:
    cur.execute('''
    INSERT INTO custo_pessoais (Categoria) 
    VALUES (?)
    ''', (categoria,))

conn.commit()

app = CTk()
app.geometry("1200x800")
set_appearance_mode('dark')

# Função para exibir os campos no menu de acordo com a opção selecionada
def menu(opcao):
    # Limpa os widgets existentes no sidebar e main_frame
    for widget in sidebar.winfo_children():
        widget.pack_forget()
    for widget in main_frame.winfo_children():
        widget.pack_forget()
        
    # Exibe o menu novamente após limpar
    CTkLabel(sidebar, text='', image=conf_img).pack()
    option_menu = CTkOptionMenu(
        sidebar,
        width=360,
        height=20,
        corner_radius=15,
        fg_color='white',
        text_color='black',
        font=('Arial Bold', 18),
        values=opcoes,
        command=menu
    )
    option_menu.set(f"{opcao}")  
    option_menu.pack(pady=(10, 20))


    if opcao == 'Receitas':
#-------------------Funçoes
        def inserir_cliente():
            nome = nome_entry.get()
            valor = int(valor_entry.get())
            juros = int(juros_entry.get()) / 100 * valor  
            total = valor + juros
            data = data_entry.get()
            entrega = (datetime.strptime(data, '%d/%m/%Y') + timedelta(days=30)).strftime('%d/%m/%Y')
            cur.execute("INSERT INTO clientes (nome, valor, juros, total, data, entrega) VALUES (?, ?, ?, ?, ?, ?)",
                        (nome, valor, juros, total, data, entrega))
            conn.commit()
            atualizar_tabela()

        def excluir_clientes():
            nome = nome_entry.get()
            data = data_entry.get()
            cur.execute("DELETE FROM clientes WHERE nome = ? AND data = ?",(nome,data))
            conn.commit()
            confirmacao = messagebox.askyesno("Confirmação", "Tem certeza de que deseja excluir cliente?")
            messagebox.showinfo("Sucesso", "Cliente excluido com sucesso")
            atualizar_tabela()
        
        def atualizar_cliente():
            nome = nome_entry.get()
            valor = int(valor_entry.get()) if valor_entry.get() else None
            juros = int(juros_entry.get()) / 100 * valor if valor else None
            total = valor + juros if valor else None
            data = data_entry.get() if data_entry.get() else None
            if valor and juros and total and data:
                entrega = (datetime.strptime(data, '%d/%m/%Y') + timedelta(days=30)).strftime('%d/%m/%Y')
                cur.execute("UPDATE clientes SET valor = ?, juros = ?, total = ?, data = ?, entrega = ? WHERE nome = ?",
                            (valor, juros, total, data, entrega, nome))
            conn.commit()

            atualizar_tabela()

        def atualizar_tabela():
            for row in tabela.get_children():
                tabela.delete(row)
            cur.execute("SELECT * FROM clientes ORDER BY SUBSTR(data, 7, 4) DESC,SUBSTR(data, 4, 2) DESC, SUBSTR(data, 1, 2) ASC ;")
            for row in cur.fetchall():
                nome, valor, juros, total, data, entrega = row
                tabela.insert("", "end", values=(nome,
                f"R$ {valor:,}".replace(",", "."),
                f"R$ {juros:,}".replace(",", "."),
                f"R$ {total:,}".replace(",", "."),
                data,entrega))
            atualizar_totais() 
   
        def atualizar_totais():
            cur.execute("SELECT SUM(valor), SUM(juros), SUM(total) FROM clientes")
            resultados = cur.fetchone()
            total_valor = resultados[0] if resultados[0] else 0
            total_juros = resultados[1] if resultados[1] else 0
            total_total = resultados[2] if resultados[2] else 0
            valor_label.configure(text=f"VALOR : R$ {total_valor:.2f}")
            juros_label.configure(text=f"JUROS : R$ {total_juros:.2f}")
            total_label.configure(text=f"TOTAL: R$ {total_total:.2f}")

        def filtrar_por_mes_clientes():
            mes_selecionado = filtro_mes.get()
            nome_selecionado = filtro_nome.get()
            if mes_selecionado == "Todos" and nome_selecionado == "":
                cur.execute("SELECT * FROM clientes ORDER BY SUBSTR(data, 7, 4) DESC, SUBSTR(data, 4, 2) DESC, SUBSTR(data, 1, 2) ASC")
            elif mes_selecionado != "Todos" and nome_selecionado == "":
                mes_num = mes_selecionado.split(" - ")[0]
                cur.execute("""
                    SELECT * 
                    FROM clientes 
                    WHERE SUBSTR(data, 4, 2) = ? 
                    ORDER BY SUBSTR(data, 7, 4) DESC, SUBSTR(data, 1, 2) ASC
                """, (mes_num,))
            elif mes_selecionado == "Todos" and nome_selecionado != "":
                cur.execute("""
                    SELECT * 
                    FROM clientes 
                    WHERE nome LIKE ? 
                    ORDER BY SUBSTR(data, 7, 4) DESC, SUBSTR(data, 4, 2) DESC, SUBSTR(data, 1, 2) ASC
                """, ('%' + nome_selecionado + '%',))
            else:
                mes_num = mes_selecionado.split(" - ")[0]
                cur.execute("""
                    SELECT * 
                    FROM clientes 
                    WHERE SUBSTR(data, 4, 2) = ? AND nome LIKE ? 
                    ORDER BY SUBSTR(data, 7, 4) DESC, SUBSTR(data, 1, 2) ASC
                """, (mes_num, '%' + nome_selecionado + '%'))
            dados_filtrados = cur.fetchall()
            
            atualizar_tabela_filtrada(dados_filtrados)
        
        def atualizar_tabela_filtrada(dados): 
            for row in tabela.get_children(): tabela.delete(row)
            for row in dados: 
                nome, valor, juros, total, data, entrega = row
                tabela.insert("", "end", values=(
                nome,
                f"R$ {valor:,}".replace(",", "."),
                f"R$ {juros:,}".replace(",", "."),
                f"R$ {total:,}".replace(",", "."),
                data,entrega)) 
            total_valor = sum(row[1] for row in dados) 
            total_juros = sum(row[2] for row in dados) 
            total_total = sum(row[3] for row in dados) 
            valor_label.configure(text=f"VALOR : R$ {total_valor:.2f}") 
            juros_label.configure(text=f"JUROS: R$ {total_juros:.2f}") 
            total_label.configure(text=f"TOTAL: R$ {total_total:.2f}")

        def limpar_historico():
            confirmacao = messagebox.askyesno("Confirmação", "Tem certeza de que deseja excluir todos os registros da tabela de clientes?")
            if confirmacao:
                cur.execute("DELETE FROM clientes")
                conn.commit()
                atualizar_tabela()
                messagebox.showinfo("Sucesso", "Todos os registros da tabela 'clientes' foram excluídos com sucesso.")

#-------------------Estrutura dentro do sidebar Receitas
        CTkLabel(sidebar, width=360, height=20, text='Nome', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        nome_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        nome_entry.pack(pady=(0, 10), padx=10, anchor='center')        
        CTkLabel(sidebar, width=360, height=20, text='Valor', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        valor_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        valor_entry.pack(pady=(0, 10), padx=10, anchor='center')       
        CTkLabel(sidebar, width=360, height=20, text='Juros', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        juros_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        juros_entry.pack(pady=(0, 10), padx=10, anchor='center')        
        CTkLabel(sidebar, width=360, height=20, text='Data', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        data_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        data_entry.pack(pady=(0, 10), padx=10, anchor='center')        
        inserir_button = CTkButton(master=sidebar, text="Inserir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=inserir_cliente)
        inserir_button.pack(pady=(10, 5), padx=10, anchor='center')       
        excluir_button = CTkButton(master=sidebar, text="Excluir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=excluir_clientes)
        excluir_button.pack(pady=(10, 5), padx=10, anchor='center')      
        atualizar_button = CTkButton(master=sidebar, text="Atualizar", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=atualizar_cliente)
        atualizar_button.pack(pady=(10, 5), padx=10, anchor='center')  
        limpar_button = CTkButton(master=sidebar, text="Limpar Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=limpar_historico)
        limpar_button.pack(pady=(10, 5), padx=10, anchor='center')
#-------------------Estrutura do Filtro
        filtro = CTkFrame(main_frame,height=50,fg_color="transparent")
        filtro.pack(fill='x',pady=(15,0),padx=27)
        filtro_nome = CTkEntry(filtro, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15,placeholder_text='Clientes')
        filtro_nome.pack(side="left", padx=(0, 5), pady=0)
        meses = ["Todos", "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril", "05 - Maio", 
         "06 - Junho", "07 - Julho", "08 - Agosto", "09 - Setembro", "10 - Outubro", 
         "11 - Novembro", "12 - Dezembro"]
        filtro_mes = CTkComboBox(filtro, values=meses, font=('Arial Bold', 14), text_color='black', fg_color='white', border_color='black',width=180, corner_radius=15)
        filtro_mes.set("Todos")
        filtro_mes.pack(side="left", padx=(0, 5), pady=0)
        procurar = CTkButton(filtro,text="PROCURAR", fg_color="black", font=("Arial Bold", 14),command=filtrar_por_mes_clientes)
        procurar.pack(side="left", padx=(10, 0), pady=10)
#-------------------Estrutura dos valores
        valores = CTkFrame(main_frame, fg_color='transparent')
        valores.pack(fill="x", padx=27, pady=(10, 0))
        valor = CTkFrame(valores, fg_color="#2A8C55", width=400, height=60)
        valor.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        valor_label = CTkLabel(valor, text="VALOR: R$ 0.00", text_color="black", font=("Arial Black", 15))
        valor_label.pack(side='left', padx=5)
        juros = CTkFrame(valores, fg_color="#9F2A2A", width=400, height=60)
        juros.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        juros_label = CTkLabel(juros, text="JUROS: R$ 0.00", text_color="black", font=("Arial Black", 15))
        juros_label.pack(side='left', padx=5)
        total = CTkFrame(valores, fg_color="#2E4C84", width=400, height=60)
        total.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        total_label = CTkLabel(total, text="Total: R$ 0.00", text_color="black", font=("Arial Black", 15))
        total_label.pack(side='left', padx=5)
#-------------------Estrutura do título
        titulo = CTkFrame(main_frame, height=50, fg_color="#5e5e5e")
        titulo.pack(anchor='n', fill='x', padx=27, pady=(29, 0))
        CTkLabel(master=titulo, text='Lista de Clientes Devedores', font=("Arial Black", 25), text_color="#FF7F00").pack(anchor="center")
#-------------------Estrutura da tabela
        tela_tabela = CTkScrollableFrame(main_frame, fg_color='transparent')
        tela_tabela.pack(expand=True, fill="both", padx=27, pady=10)  
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 18, "bold"), background="#2F4F4F", foreground="black")
        style.configure("Treeview", rowheight=20, font=("Arial", 15), borderwidth=1, relief="solid")
        style.map("Treeview", background=[('selected', '#347083')])  
        tabela = ttk.Treeview(tela_tabela, columns=('Nome', 'Valor', 'Juros', 'Total', 'Data', 'Entrega'), show='headings', height=50)
        tabela.column('Nome', width=250)
        tabela.column('Valor', width=200, anchor=CENTER)
        tabela.column('Juros', width=150, anchor=CENTER)
        tabela.column('Total', width=100, anchor=CENTER)
        tabela.column('Data', width=100, anchor=CENTER)
        tabela.column('Entrega', width=100, anchor=CENTER)
        for col in ('Nome', 'Valor', 'Juros', 'Total', 'Data', 'Entrega'):
            tabela.heading(col, text=col)
        tabela.pack(fill='both', expand=True, padx=5, pady=5)

    elif opcao == 'Fluxo de Caixa':
        def inserir_dados():
            data = data_entry.get()
            entrada =int(entrada_entry.get())
            saida = int(saida_entry.get())  
            saldo = entrada - saida
            cur.execute("INSERT INTO fluxo_de_caixa (data,entrada,saida,saldo) VALUES (?, ?, ?, ?)",
                        (data,entrada,saida,saldo))
            conn.commit()
            atualizar_tabela()

        def atualizar_tabela():
            for row in tabela.get_children():
                tabela.delete(row)
            cur.execute("SELECT * FROM fluxo_de_caixa ORDER BY SUBSTR(data, 7, 4) DESC,SUBSTR(data, 4, 2) DESC, SUBSTR(data, 1, 2) ASC ;")
            for row in cur.fetchall():
                data,entrada,saida,saldo = row
                tabela.insert("", "end", values=(data,
                                f"R$ {entrada:,}".replace(",", "."),
                                f"R$ {saida:,}".replace(",", "."),
                                f"R$ {saldo:,}".replace(",", "."),
                                ))
            atualizar_totais() 

        def atualizar_totais():
            cur.execute("SELECT SUM(entrada), SUM(saida), SUM(saldo) FROM fluxo_de_caixa")
            resultados = cur.fetchone()
            total_valor = resultados[0] if resultados[0] else 0
            total_juros = resultados[1] if resultados[1] else 0
            total_total = resultados[2] if resultados[2] else 0
            entrada_label.configure(text=f"ENTRADA : R$ {total_valor:.2f}")
            saida_label.configure(text=f"SAIDA : R$ {total_juros:.2f}")
            saldo_label.configure(text=f"SALDO: R$ {total_total:.2f}")

        def filtrar_por_mes():
            mes_selecionado = filtro_mes.get()
            if mes_selecionado == "Todos":
                cur.execute("SELECT * FROM fluxo_de_caixa ORDER BY SUBSTR(data, 7, 4) DESC, SUBSTR(data, 4, 2) DESC, SUBSTR(data, 1, 2) ASC")
            else:
                mes_num = mes_selecionado.split(" - ")[0]  
                cur.execute("""
                    SELECT * 
                    FROM fluxo_de_caixa 
                    WHERE SUBSTR(data, 4, 2) = ? 
                    ORDER BY SUBSTR(data, 7, 4) DESC, SUBSTR(data, 1, 2) ASC
                """, (mes_num,))
            dados_filtrados = cur.fetchall()
            atualizar_tabela_filtrada(dados_filtrados)

        def atualizar_tabela_filtrada(dados):
            for row in tabela.get_children():
                tabela.delete(row)
            for row in dados:
               data, entrada,saida,saldo = row
               tabela.insert("", "end", values=(data,
                f"R$ {entrada:,}".replace(",", "."),
                f"R$ {saida:,}".replace(",", "."),
                f"R$ {saldo:,}".replace(",", ".")
                ))
            total_entrada = sum(row[1] for row in dados)
            total_saida = sum(row[2] for row in dados)
            total_saldo = sum(row[3] for row in dados)
            entrada_label.configure(text=f"ENTRADA : R$ {total_entrada:.2f}")
            saida_label.configure(text=f"SAÍDA: R$ {total_saida:.2f}")
            saldo_label.configure(text=f"SALDO: R$ {total_saldo:.2f}")

            

        def limpar_historico():
            confirmacao = messagebox.askyesno("Confirmação", "Tem certeza de que deseja excluir todos os registros da tabela de fluxo_de_caixa?")
            if confirmacao:
                cur.execute("DELETE FROM fluxo_de_caixa")
                conn.commit()
                atualizar_tabela()
                messagebox.showinfo("Sucesso", "Todos os registros da tabela 'fluxo_de_caixa' foram excluídos com sucesso.")

#-------------------Estrutura dentro do sidebar para Fluxo de Caixa
        CTkLabel(sidebar, width=360, height=20, text='Data', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        data_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        data_entry.pack(pady=(0, 10), padx=10, anchor='center')
        CTkLabel(sidebar, width=360, height=20, text='Entrada', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        entrada_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        entrada_entry.pack(pady=(0, 10), padx=10, anchor='center')        
        CTkLabel(sidebar, width=360, height=20, text='Saída', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        saida_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        saida_entry.pack(pady=(0, 10), padx=10, anchor='center')   
        inserir_button = CTkButton(master=sidebar, text="Inserir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=inserir_dados)
        inserir_button.pack(pady=(10, 5), padx=10, anchor='center')       
        historico_button = CTkButton(master=sidebar, text="Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=atualizar_tabela)
        historico_button.pack(pady=(10, 5), padx=10, anchor='center')       
        limpar_button = CTkButton(master=sidebar, text="Limpar Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=limpar_historico)
        limpar_button.pack(pady=(10, 5), padx=10, anchor='center')
        #-------------------Estrutura do Filtro
        filtro = CTkFrame(main_frame,height=50,fg_color="transparent")
        filtro.pack(fill='x',pady=(15,0),padx=27)
        meses = ["Todos", "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril", "05 - Maio", 
         "06 - Junho", "07 - Julho", "08 - Agosto", "09 - Setembro", "10 - Outubro", 
         "11 - Novembro", "12 - Dezembro"]
        filtro_mes = CTkComboBox(filtro, values=meses, font=('Arial Bold', 14), text_color='black', fg_color='white', border_color='black',width=180, corner_radius=15)
        filtro_mes.set("Todos")
        filtro_mes.pack(side="left", padx=(0, 5), pady=0)
        procurar = CTkButton(filtro, text="PROCURAR", fg_color="black", font=("Arial Bold", 14),command=filtrar_por_mes)
        procurar.pack(side="left", padx=(10, 0), pady=10)
#-------------------Estrutura do valores
        valores = CTkFrame(main_frame,fg_color='transparent')
        valores.pack(fill="x", padx=27, pady=(10, 0))
        entrada = CTkFrame(valores, fg_color="#2A8C55", width=400, height=60)
        entrada.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        entrada_label = CTkLabel(entrada, text="Entrada: R$ 0.00", text_color="black", font=("Arial Black", 15))
        entrada_label.pack(side='left', padx=5)
        saida = CTkFrame(valores, fg_color="#9F2A2A", width=400, height=60)
        saida.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        saida_label = CTkLabel(saida, text="Saída: R$ 0.00", text_color="black", font=("Arial Black", 15))
        saida_label.pack(side='left', padx=5)
        saldo = CTkFrame(valores, fg_color="#2E4C84", width=400, height=60)
        saldo.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        saldo_label = CTkLabel(saldo, text="Saldo: R$ 0.00", text_color="black", font=("Arial Black", 15))
        saldo_label.pack(side='left', padx=5)
 #-------------------Estrutura do titulo
        titulo = CTkFrame(main_frame,height=50,fg_color="#5e5e5e")
        titulo.pack(anchor='n',fill='x',padx=27,pady=(29,0))
        CTkLabel(titulo,text='Fluxo de Caixa Historico',font=("Arial Black", 25),text_color="#FF7F00").pack(anchor="center")      
 #-------------------Estrutura da Tabela
        tela_tabela = CTkScrollableFrame(main_frame,fg_color='transparent')
        tela_tabela.pack(expand=True,fill="both", padx=27, pady=10 )
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 18, "bold"), background="#2F4F4F", foreground="black")
        style.configure("Treeview", rowheight=20, font=("Arial", 15), borderwidth=1, relief="solid")
        style.map("Treeview", background=[('selected', '#347083')])
        tabela = ttk.Treeview(tela_tabela, columns=( 'Data', 'Entrada','Saída','Saldo'), show='headings', height=50) 
        tabela.column('Data', width=100)
        tabela.column('Entrada', width=100,anchor=CENTER)
        tabela.column('Saída', width=100,anchor=CENTER)
        tabela.column('Saldo', width=100,anchor=CENTER)
        

        for col in ('Data', 'Entrada','Saída','Saldo'): tabela.heading(col, text=col) 
        tabela.pack(fill = 'both' ,expand=True,padx=5,pady=5)

    elif opcao == 'Parcelados e Cartões':

        def inserir_cliente():
            nome = nome_entry.get()
            valor = int(valor_entry.get())
            total = int(total_entry.get())
            vl_par = int(vl_parcelas_entry.get())
            qnt_par = int(qt_parcelas_entry.get())
            data = data_entry.get()
            lucro = total - valor
            data_inicio = datetime.strptime(data, '%d/%m/%Y')
            termino = data_inicio + relativedelta(months=qnt_par)
            termino = termino.strftime('%d/%m/%Y')
            cur.execute("INSERT INTO parcelados_cartoes (nome, valor, lucro, total, qnt_par, vl_par, data, termino) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (nome, valor, lucro, total, qnt_par, vl_par, data, termino))
            conn.commit()
            atualizar_tabela()

        def excluir_clientes():
            nome = nome_entry.get()
            data = data_entry.get()
            cur.execute("DELETE FROM parcelados_cartoes WHERE nome = ? AND data = ?",(nome,data))
            conn.commit()
            atualizar_tabela()

        def atualizar_cliente():
            nome = nome_entry.get()
            valor = int(valor_entry.get()) if valor_entry.get() else None
            total = int(total_entry.get()) if total_entry.get() else None
            qnt_par = int(qt_parcelas_entry.get()) if qt_parcelas_entry.get() else None
            vl_par = int(vl_parcelas_entry.get()) if vl_parcelas_entry.get() else None
            data = data_entry.get() if data_entry.get() else None
            lucro = total - valor if valor is not None and total is not None else None  
            termino = None
            if qnt_par and data:
                    data_inicio = datetime.strptime(data, '%d/%m/%Y')
                    termino = data_inicio + relativedelta(months=qnt_par)
                    termino = termino.strftime('%d/%m/%Y') 
            cur.execute("""
                    UPDATE parcelados_cartoes 
                    SET valor = ?, total = ?, qnt_par = ?, vl_par = ?, data = ?, termino = ?, lucro = ? 
                    WHERE nome = ?""",
                    (valor, total, qnt_par, vl_par, data, termino, lucro, nome))
            conn.commit()
            atualizar_tabela()

        def atualizar_tabela():
            # Limpa os dados atuais da tabela
            for row in tabela.get_children():
                tabela.delete(row)
            cur.execute("""
                SELECT * FROM parcelados_cartoes 
                ORDER BY 
                    SUBSTR(data, 7, 4) DESC,
                    SUBSTR(data, 4, 2) DESC,
                    SUBSTR(data, 1, 2) ASC;
            """)
            for row in cur.fetchall():
                nome, valor, lucro, total, vl_par, qnt_par, data, termino = row
                tabela.insert("", "end", values=(
                    nome,
                    f"R$ {valor:,}".replace(",", "."),
                    f"R$ {lucro:,}".replace(",", "."),
                    f"R$ {total:,}".replace(",", "."),
                    vl_par,qnt_par,data,
                    termino))
                atualizar_totais() 

        def atualizar_totais():
            cur.execute("SELECT SUM(valor), SUM(LUCRO), SUM(total) FROM parcelados_cartoes")
            resultados = cur.fetchone()
            total_valor = resultados[0] if resultados[0] else 0
            total_lucro = resultados[1] if resultados[1] else 0
            total_total = resultados[2] if resultados[2] else 0
            valor_label.configure(text=f"VALOR : R$ {total_valor:.2f}")
            lucros_label.configure(text=f"LUCRO : R$ {total_lucro:.2f}")
            total_label.configure(text=f"TOTAL: R$ {total_total:.2f}")

        def limpar_historico():
            confirmacao = messagebox.askyesno("Confirmação", "Tem certeza de que deseja excluir todos os registros da tabela de clientes?")
            if confirmacao:
                cur.execute("DELETE FROM parcelados_cartoes")
                conn.commit()
                atualizar_tabela()
                messagebox.showinfo("Sucesso", "Todos os registros da tabela 'clientes' foram excluídos com sucesso.")

#-------------------Adiciona os campos para "Parcelados"
        CTkLabel(sidebar, width=360, height=20, text='Nome', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        nome_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        nome_entry.pack(pady=(0, 10), padx=10, anchor='center')
        CTkLabel(sidebar, width=360, height=20, text='Valor', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        valor_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        valor_entry.pack(pady=(0, 10), padx=10, anchor='center')
        CTkLabel(sidebar, width=360, height=20, text='Total', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        total_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        total_entry.pack(pady=(0, 10), padx=10, anchor='center')
        CTkLabel(sidebar, width=360, height=20, text='Qnt. Parcelas', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        qt_parcelas_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        qt_parcelas_entry.pack(pady=(0, 10), padx=10, anchor='center')
        CTkLabel(sidebar, width=360, height=20, text='Vl. Parcelas', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        vl_parcelas_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        vl_parcelas_entry .pack(pady=(0, 10), padx=10, anchor='center')        
        CTkLabel(sidebar, width=360, height=20, text='Data', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        data_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        data_entry.pack(pady=(0, 10), padx=10, anchor='center')
        inserir_button = CTkButton(master=sidebar, text="Inserir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=inserir_cliente)
        inserir_button.pack(pady=(10, 5), padx=10, anchor='center')
        excluir_button = CTkButton(master=sidebar, text="Excluir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=excluir_clientes)
        excluir_button.pack(pady=(10, 5), padx=10, anchor='center')
        atualizar_button = CTkButton(master=sidebar, text="Atualizar/Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=atualizar_cliente)
        atualizar_button.pack(pady=(10, 5), padx=10, anchor='center')
        limpar_button = CTkButton(master=sidebar, text="Limpar Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=limpar_historico)
        limpar_button.pack(pady=(10,5), padx=0, anchor='center')
#-------------------Estrutura do valores
        valores = CTkFrame(main_frame, fg_color='transparent')
        valores.pack(fill="x", padx=27, pady=(10, 0))
        valor = CTkFrame(valores, fg_color="#2A8C55", width=400, height=60)
        valor.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        valor_label = CTkLabel(valor, text="VALOR: R$ 0.00", text_color="black", font=("Arial Black", 15))
        valor_label.pack(side='left', padx=5)
        lucros = CTkFrame(valores, fg_color="#9F2A2A", width=400, height=60)
        lucros.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        lucros_label = CTkLabel(lucros, text="LUCROS: R$ 0.00", text_color="black", font=("Arial Black", 15))
        lucros_label.pack(side='left', padx=5)
        total = CTkFrame(valores, fg_color="#2E4C84", width=400, height=60)
        total.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        total_label = CTkLabel(total, text="Total: R$ 0.00", text_color="black", font=("Arial Black", 15))
        total_label.pack(side='left', padx=5)
#-------------------Estrutura do titulo
        titulo = CTkFrame(main_frame,height=50,fg_color="#5e5e5e")
        titulo.pack(anchor='n',fill='x',padx=27,pady=(29,0))
        CTkLabel(master=titulo,text='Lista de Clientes Devedores Parcelados e Cartões',font=("Arial Black", 25),text_color="#FF7F00").pack(anchor="center")
#-------------------Estrutura da tabela
        tela_tabela = CTkScrollableFrame(main_frame, fg_color='transparent')
        tela_tabela.pack(expand=True, fill="both", padx=27, pady=10)  
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 18, "bold"), background="#2F4F4F", foreground="black")
        style.configure("Treeview", rowheight=20, font=("Arial", 15), borderwidth=1, relief="solid")
        style.map("Treeview", background=[('selected', '#347083')])  
        tabela = ttk.Treeview(tela_tabela, columns=('Nome', 'Valor', 'Lucro', 'Total','Qt. Parcelas','Vl. Parcelas' ,'Data', 'Termino'), show='headings', height=50)
        tabela.column('Nome', width=250)
        tabela.column('Valor', width=200, anchor=CENTER)
        tabela.column('Lucro', width=150, anchor=CENTER)
        tabela.column('Total', width=100, anchor=CENTER)
        tabela.column('Qt. Parcelas', width=100, anchor=CENTER)
        tabela.column('Vl. Parcelas', width=100, anchor=CENTER)
        tabela.column('Data', width=100, anchor=CENTER)
        tabela.column('Termino', width=100, anchor=CENTER)
        for col in ('Nome', 'Valor', 'Lucro', 'Total','Qt. Parcelas','Vl. Parcelas' ,'Data', 'Termino'):
            tabela.heading(col, text=col)
        tabela.pack(fill='both', expand=True, padx=5, pady=5)

    elif opcao == 'Custo Pessoal':

        def inserir_valor():
            categoria = categoria_menu.get()  
            mes = categoria_mes.get()  
            valor = valor_entry.get() 
            try:
                valor = float(valor)  
            except ValueError:
                messagebox.showerror("Erro", "Por favor, insira um valor numérico válido.")
                return
            cur.execute(f"UPDATE 'custo_pessoais' SET '{mes}' = ? WHERE Categoria = ?", (valor, categoria))
            conn.commit()  
            valor_entry.delete(0, 'end')  
            atualizar_tabela()  

        def calcular_receita_despesa_saldo():
            try:
                cur.execute("""
                    SELECT Janeiro, Fevereiro, Março, Abril, Maio, Junho, Julho, Agosto, Setembro, Outubro, Novembro, Dezembro 
                    FROM custo_pessoais WHERE Categoria = 'Salários'
                """)
                salario = sum(sum(row) for row in cur.fetchall())
                cur.execute("""
                    SELECT Janeiro, Fevereiro, Março, Abril, Maio, Junho, Julho, Agosto, Setembro, Outubro, Novembro, Dezembro 
                    FROM custo_pessoais WHERE Categoria = 'Investimentos'
                """)
                investimento = sum(sum(row) for row in cur.fetchall())
                receita = salario + investimento
                cur.execute("""
                    SELECT Janeiro, Fevereiro, Março, Abril, Maio, Junho, Julho, Agosto, Setembro, Outubro, Novembro, Dezembro 
                    FROM custo_pessoais WHERE Categoria NOT IN ('Salários', 'Investimentos')
                """)
                despesa = sum(sum(row) for row in cur.fetchall())              
                saldo = receita - despesa
                receita_label.configure(text=f"Receita: R$ {receita:.2f}")
                despesa_label.configure(text=f"Despesa: R$ {despesa:.2f}")
                saldo_label.configure(text=f"Saldo: R$ {saldo:.2f}")
            except sqlite3.Error as e:
                messagebox.showerror("Erro no banco de dados", f"Erro: {e}")

        def formatar_valor(valor):
            """
            Formata um número para o padrão brasileiro sem centavos: R$ 1.000
            """
            if valor is None:  
                return "R$ 0"
            return f"R$ {int(valor):,}".replace(",", ".")

        def atualizar_tabela():
            try:
                # Limpa os dados existentes na tabela
                for row in tabela.get_children():
                    tabela.delete(row)
                cur.execute("SELECT * FROM custo_pessoais") 
                rows = cur.fetchall()
                for row in rows:
                    categoria, Janeiro, Fevereiro, Março, Abril, Maio, Junho, Julho, Agosto, Setembro, Outubro, Novembro, Dezembro = row
                    tabela.insert("", "end", values=(
                        categoria,
                        formatar_valor(Janeiro),   
                        formatar_valor(Fevereiro),
                        formatar_valor(Março),
                        formatar_valor(Abril),
                        formatar_valor(Maio),
                        formatar_valor(Junho),
                        formatar_valor(Julho),
                        formatar_valor(Agosto),
                        formatar_valor(Setembro),
                        formatar_valor(Outubro),
                        formatar_valor(Novembro),
                        formatar_valor(Dezembro)
                    ))
                calcular_receita_despesa_saldo()

            except Exception as e:
                print(f"Erro ao atualizar tabela: {e}")

        def limpar_historico():
            confirmar = messagebox.askyesno("Confirmar", "Tem certeza de que deseja limpar o histórico?")
            if confirmar:
                try:
                    cur.execute("""
                        UPDATE custo_pessoais SET Janeiro = 0, Fevereiro = 0, Março = 0, Abril = 0, Maio = 0, Junho = 0, 
                                                Julho = 0, Agosto = 0, Setembro = 0, Outubro = 0, Novembro = 0, Dezembro = 0
                    """)
                    conn.commit()  
                    atualizar_tabela()
                except sqlite3.Error as e:
                    messagebox.showerror("Erro no banco de dados", f"Erro: {e}")

        def calcular_receita_despesa_saldo_por_mes():
            mes_selecionado = filtro_mes.get() 
            if mes_selecionado == "Todos":
                
                calcular_receita_despesa_saldo()
                return
            mes = mes_selecionado.split(" - ")[1]

            try:
                cur.execute(f"SELECT COALESCE({mes}, 0) FROM custo_pessoais WHERE Categoria = 'Salários'")
                salario = sum(row[0] for row in cur.fetchall())
                cur.execute(f"SELECT COALESCE({mes}, 0) FROM custo_pessoais WHERE Categoria = 'Investimentos'")
                investimento = sum(row[0] for row in cur.fetchall())
                receita = salario + investimento
                cur.execute(f"""
                    SELECT COALESCE({mes}, 0) FROM custo_pessoais 
                    WHERE Categoria NOT IN ('Salários', 'Investimentos')
                """)
                despesa = sum(row[0] for row in cur.fetchall())
                saldo = receita - despesa
                receita_label.configure(text=f"Receita ({mes}): R$ {receita:.2f}")
                despesa_label.configure(text=f"Despesa ({mes}): R$ {despesa:.2f}")
                saldo_label.configure(text=f"Saldo ({mes}): R$ {saldo:.2f}")
            except sqlite3.Error as e:
                messagebox.showerror("Erro no banco de dados", f"Erro: {e}")
        categoria = ['Salários', 
             'Investimentos',
             'Seguro do Carro',
             'Supermercado',
             'Internet',
             'FGTS',
             'Luz',
             'Dieta',
             'Gás',
             'Cabelo',
             'Combustivel de Carro',
             'Manutenção do carro',
             'IPVA',
             'Medico',
             'Outros']
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        CTkLabel(sidebar, width=360, height=20, text='Categoria', font=('Arial Bold', 12)).pack(pady=(10, 0), anchor='center', padx=10)
        categoria_menu = CTkOptionMenu(sidebar,width=360,height=20,values=categoria,font=('Arial Bold', 12), fg_color='white', text_color='black', corner_radius=15)
        categoria_menu.pack(pady=(0, 10), padx=10, anchor='center')
        CTkLabel(sidebar, width=360, height=20, text='Meses', font=('Arial Bold', 12)).pack(pady=(10, 0), anchor='center', padx=10)
        categoria_mes = CTkOptionMenu(sidebar,width=360,height=20,values=meses,font=('Arial Bold', 12), fg_color='white', text_color='black', corner_radius=15)
        categoria_mes.pack(pady=(0, 10), padx=10, anchor='center')
        CTkLabel(sidebar, width=360, height=20, text='Valor', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        valor_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        valor_entry.pack(pady=(0, 10), padx=10, anchor='center')
        inserir_button = CTkButton(master=sidebar, text="Inserir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=inserir_valor)
        inserir_button.pack(pady=(10, 5), padx=10, anchor='center') 
        atualizar_button = CTkButton(master=sidebar, text="Atualizar", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=atualizar_tabela)
        atualizar_button.pack(pady=(10, 5), padx=10, anchor='center')
        limpar_button = CTkButton(master=sidebar, text="Limpar Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=limpar_historico)
        limpar_button.pack(pady=(10, 5), padx=10, anchor='center')

        #-------------------Estrutura do Filtro
        filtro = CTkFrame(main_frame,height=50,fg_color="transparent")
        filtro.pack(fill='x',pady=(15,0),padx=27)
        meses = ["Todos", "01 - Janeiro", "02 - Fevereiro", "03 - Março", "04 - Abril", "05 - Maio", 
         "06 - Junho", "07 - Julho", "08 - Agosto", "09 - Setembro", "10 - Outubro", 
         "11 - Novembro", "12 - Dezembro"]
        filtro_mes = CTkComboBox(filtro, values=meses, font=('Arial Bold', 14), text_color='black', fg_color='white', border_color='black',width=180, corner_radius=15)
        filtro_mes.set("Todos")
        filtro_mes.pack(side="left", padx=(0, 5), pady=0)
        procurar = CTkButton(filtro, text="PROCURAR", fg_color="black", font=("Arial Bold", 14),command=calcular_receita_despesa_saldo_por_mes)
        procurar.pack(side="left", padx=(10, 0), pady=10)

        #-------------------Estrutura do valores
        valores = CTkFrame(main_frame,fg_color='transparent')
        valores.pack(fill="x", padx=27, pady=(10, 0))
        receita = CTkFrame(valores, fg_color="#2A8C55", width=400, height=60)
        receita.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        receita_label = CTkLabel(receita, text="Receita: R$ 0.00", text_color="black", font=("Arial Black", 15))
        receita_label.pack(side='left', padx=5)
        despesa= CTkFrame(valores, fg_color="#9F2A2A", width=400, height=60)
        despesa.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        despesa_label = CTkLabel(despesa, text="Despesa: R$ 0.00", text_color="black", font=("Arial Black", 15))
        despesa_label.pack(side='left', padx=5)
        saldo = CTkFrame(valores, fg_color="#2E4C84", width=400, height=60)
        saldo.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        saldo_label = CTkLabel(saldo, text="Saldo: R$ 0.00", text_color="black", font=("Arial Black", 15))
        saldo_label.pack(side='left', padx=5)

        #-------------------Estrutura da Tabela
        tela_tabela = CTkScrollableFrame(main_frame, fg_color='transparent')
        tela_tabela.pack(expand=True, fill="both", padx=27, pady=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 18, "bold"), background="#2F4F4F", foreground="black")
        style.configure("Treeview", rowheight=20, font=("Arial", 15), borderwidth=1, relief="solid")
        style.map("Treeview", background=[('selected', '#347083')])
        tabela = ttk.Treeview(
            tela_tabela, 
            columns=('Categoria', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'), 
            show='headings', 
            height=50)
        tabela.column('Categoria', width=250)
        tabela.column('Janeiro', width=200, anchor=CENTER)
        tabela.column('Fevereiro', width=200, anchor=CENTER)
        tabela.column('Março', width=200, anchor=CENTER)
        tabela.column('Abril', width=200, anchor=CENTER)
        tabela.column('Maio', width=200, anchor=CENTER)
        tabela.column('Junho', width=200, anchor=CENTER)
        tabela.column('Julho', width=200, anchor=CENTER)
        tabela.column('Agosto', width=200, anchor=CENTER)
        tabela.column('Setembro', width=200, anchor=CENTER)
        tabela.column('Outubro', width=200, anchor=CENTER)
        tabela.column('Novembro', width=200, anchor=CENTER)
        tabela.column('Dezembro', width=200, anchor=CENTER)
        for col in ('Categoria', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'):
            tabela.heading(col, text=col)
        for cat in categoria:
            tabela.insert('', 'end', values=[cat] + [''] * 12)
            tabela.pack(fill='both', expand=True, padx=5, pady=5)

    elif opcao == 'Investimentos Pessoais':

        def inserir_dados():
            instituicao = instituicao_entry.get()
            valor = int(valor_entry.get())
            total = int(total_entry.get())
            juros = total-valor
            data = data_entry.get()
            cur.execute("INSERT INTO investimentos_pessoais (instituicao, valor,total, juros,  data) VALUES (?, ?, ?, ?, ?)",
                        (instituicao, valor,total, juros,  data))
            conn.commit()
            atualizar_tabela()

        def excluir_dados():
            instituicao = instituicao_entry.get()
            data = data_entry.get()
            cur.execute("DELETE FROM investimentos_pessoais WHERE instituicao = ? AND data = ?",(instituicao,data))
            conn.commit()
            atualizar_tabela()
        
        def atualizar_dados():
            instituicao = instituicao_entry.get()
            valor = int(valor_entry.get()) if valor_entry.get() else None
            total = int(total_entry.get()) if valor else None

            juros = total-valor  if valor else None
            data = data_entry.get() if data_entry.get() else None
            if valor and juros and total and data:
                cur.execute("UPDATE investimentos_pessoais SET valor = ?, total = ? , juros = ?,  data = ? WHERE instituicao = ?",
                            (valor,total, juros,  data,  instituicao))
            conn.commit()
            atualizar_tabela()

        def atualizar_tabela():
            for row in tabela.get_children():
                tabela.delete(row)
            cur.execute("SELECT * FROM investimentos_pessoais ORDER BY SUBSTR(data, 7, 4) DESC,SUBSTR(data, 4, 2) DESC, SUBSTR(data, 1, 2) ASC ;")
            for row in cur.fetchall():
                instituicao, valor, juros, total, data = row
                tabela.insert("", "end", values=(
                instituicao,
                f"R$ {valor:,}".replace(",", "."),
                f"R$ {juros:,}".replace(",", "."),
                f"R$ {total:,}".replace(",", "."),
                data))
            atualizar_totais() 
   
        def atualizar_totais():
            cur.execute("SELECT SUM(valor), SUM(juros), SUM(total) FROM investimentos_pessoais")
            resultados = cur.fetchone()
            total_valor = resultados[0] if resultados[0] else 0
            total_juros = resultados[1] if resultados[1] else 0
            total_total = resultados[2] if resultados[2] else 0
            valor_label.configure(text=f"VALOR : R$ {total_valor:.2f}")
            juros_label.configure(text=f"JUROS : R$ {total_juros:.2f}")
            total_label.configure(text=f"TOTAL: R$ {total_total:.2f}")

        def limpar_historico():
            confirmacao = messagebox.askyesno("Confirmação", "Tem certeza de que deseja excluir todos os registros da tabela de investimentos_pessoais?")
            if confirmacao:
                cur.execute("DELETE FROM investimentos_pessoais")
                conn.commit()
                atualizar_tabela()
                messagebox.showinfo("Sucesso", "Todos os registros da tabela 'investimentos_pessoais' foram excluídos com sucesso.")

        #-------------------Estrutura dentro do sidebar Receitas
        CTkLabel(sidebar, width=360, height=20, text='Instituição', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        instituicao_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        instituicao_entry.pack(pady=(0, 10), padx=10, anchor='center')   
        CTkLabel(sidebar, width=360, height=20, text='Valor', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        valor_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        valor_entry.pack(pady=(0, 10), padx=10, anchor='center')     
        CTkLabel(sidebar, width=360, height=20, text='Total', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        total_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        total_entry.pack(pady=(0, 10), padx=10, anchor='center')        
        CTkLabel(sidebar, width=360, height=20, text='Data', font=('Arial Bold', 14)).pack(pady=(10, 0), anchor='center', padx=10)
        data_entry = CTkEntry(sidebar, width=360, height=20, font=('Arial Bold', 18), text_color='black', fg_color='white', border_color='black', corner_radius=15)
        data_entry.pack(pady=(0, 10), padx=10, anchor='center')    
        inserir_button = CTkButton(master=sidebar, text="Inserir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=inserir_dados)
        inserir_button.pack(pady=(10, 5), padx=10, anchor='center')      
        excluir_button = CTkButton(master=sidebar, text="Excluir", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=excluir_dados)
        excluir_button.pack(pady=(10, 5), padx=10, anchor='center')  
        atualizar_button = CTkButton(master=sidebar, text="Atualizar/Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=atualizar_dados)
        atualizar_button.pack(pady=(10, 5), padx=10, anchor='center')  
        limpar_button = CTkButton(master=sidebar, text="Limpar Histórico", fg_color='transparent', font=("Arial Bold", 14), hover_color='#111111',command=limpar_historico)
        limpar_button.pack(pady=(10, 5), padx=10, anchor='center')
#-------------------Estrutura dos valores
        valores = CTkFrame(main_frame, fg_color='transparent')
        valores.pack(fill="x", padx=27, pady=(10, 0))
        valor = CTkFrame(valores, fg_color="#2A8C55", width=400, height=60)
        valor.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        valor_label = CTkLabel(valor, text="VALOR: R$ 0.00", text_color="black", font=("Arial Black", 15))
        valor_label.pack(side='left', padx=5)
        juros = CTkFrame(valores, fg_color="#9F2A2A", width=400, height=60)
        juros.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        juros_label = CTkLabel(juros, text="JUROS: R$ 0.00", text_color="black", font=("Arial Black", 15))
        juros_label.pack(side='left', padx=5)
        total = CTkFrame(valores, fg_color="#2E4C84", width=400, height=60)
        total.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        total_label = CTkLabel(total, text="Total: R$ 0.00", text_color="black", font=("Arial Black", 15))
        total_label.pack(side='left', padx=5)
#-------------------Estrutura do título
        titulo = CTkFrame(main_frame, height=50, fg_color="#5e5e5e")
        titulo.pack(anchor='n', fill='x', padx=27, pady=(29, 0))
        CTkLabel(master=titulo, text='Investimentos Pessoais', font=("Arial Black", 25), text_color="#FF7F00").pack(anchor="center")
#-------------------Estrutura da tabela
        tela_tabela = CTkScrollableFrame(main_frame, fg_color='transparent')
        tela_tabela.pack(expand=True, fill="both", padx=27, pady=10)  
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Arial", 18, "bold"), background="#2F4F4F", foreground="black")
        style.configure("Treeview", rowheight=20, font=("Arial", 15), borderwidth=1, relief="solid")
        style.map("Treeview", background=[('selected', '#347083')])  
        tabela = ttk.Treeview(tela_tabela, columns=('Instituição', 'Valor', 'Juros', 'Total', 'Data'), show='headings', height=50)
        tabela.column('Instituição', width=250)
        tabela.column('Valor', width=200, anchor=CENTER)
        tabela.column('Juros', width=150, anchor=CENTER)
        tabela.column('Total', width=100, anchor=CENTER)
        tabela.column('Data', width=100, anchor=CENTER)
        for col in ('Instituição', 'Valor', 'Juros', 'Total', 'Data'):
            tabela.heading(col, text=col)
        tabela.pack(fill='both', expand=True, padx=5, pady=5)


#-----------------Configurações da sidebar
sidebar = CTkFrame(app, width=360, height=650, fg_color='#3D0000')
sidebar.pack_propagate(0)
sidebar.pack(fill='y', anchor='w', side='left')

#----------------------Carrega e redimensiona a imagem
img = Image.open('macaco.png')
sidebar_width = 360
img = img.resize((sidebar_width, int(img.height * (sidebar_width / img.width))))
conf_img = CTkImage(dark_image=img, light_image=img, size=(sidebar_width, img.height))
CTkLabel(sidebar, text='', image=conf_img).pack()

#---------------------Configurações do menu de opções
opcoes = ['Receitas', 'Fluxo de Caixa','Parcelados e Cartões', 'Custo Pessoal','Investimentos Pessoais' ]
option_menu = CTkOptionMenu(
    sidebar,
    width=360,
    height=20,
    corner_radius=15,
    fg_color='white',
    text_color='black',
    font=('Arial Bold', 18),
    values=opcoes,
    command=menu)
option_menu.set("Selecione a opção") 
option_menu.pack(pady=(10, 20))

#-----------Configurações do main_frame
main_frame = CTkFrame(app, fg_color='#5e5e5e', corner_radius=20)
main_frame.pack(fill='both', expand=True, padx=5, pady=5)

app.mainloop()