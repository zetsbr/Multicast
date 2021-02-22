#Author: João Vitor de Andrade Porto RA1702
#Código feito com base na explicação de multicast do site pymotw
#link: https://pymotw.com/2/socket/multicast.html
#Esta classe é a implementação de um processo que será externo ao multicast
import socket
import threading
import time
import tkinter as tk
#definição da do socket e endereco do servidor
s = socket.socket()
host = '{}'.format(socket.gethostbyname(socket.gethostname()))
port = 9998
#função para conectar o cliente externo a socket do líder dentro do multicast
def connect():
    global host
    global port
    global s
    s.connect((host, port))
    s.setblocking(1)
    s.settimeout(2)
    print('conectado a {}'.format(host))
#método de recebimento de mensagens e finalização do código caso o líder feche o socket
def alive_response():
    global s
    global i
    while True:
        try:
            print('recebendo mensagem')
            s.sendto((' ').encode(),(host,port))
            data = s.recv(20480)
            if(data and data.decode("utf-8")!=' '):
                sv2.set(data.decode("utf-8"))
                print(data)
            data=''
        except:
            print('conexao encerrada')
            i.destroy()
            break
#método para o envio de mensagem através da interface com a tag E_ para processos externo     
def send_message():
    global s
    global sv1
    msg=sv1.get()
    if(not(msg.startswith('I2E_')) and not(msg.startswith('Ele_')) and not(msg.startswith('Lid_'))):
        s.sendto(('E2I_'+msg).encode(),(host,port))
        print(msg)
#conexão e início da comunicação
connect()
t = threading.Thread(target=alive_response)
t.daemon = True
t.start()
s.sendto(' '.encode(),(host,port))
#interface principal do programa para envio e recebimento de mensagens de forma inteligível (sem isso vira uma sopa de letras difícil,de ler)
i=tk.Tk()
sv1=tk.StringVar()
sv2=tk.StringVar()
sv3=tk.StringVar()
sv3.set(str(True))
b=tk.Button(i,text='send message',command=send_message)
l1=tk.Label(i,text='ENVIO')
l2=tk.Label(i,text='RECEBIMENTO')
l4=tk.Label(i,text='')
l5=tk.Label(i,text='')
e1=tk.Entry(i,textvariable=sv1,width=20)
e2=tk.Entry(i,textvariable=sv2,width=20)
e3=tk.Entry(i,textvariable=sv3,width=5)
l3=tk.Label(i,text='Externo')
#ativação da interface com os componentes em suas devidas posições
i.geometry('270x200')
e3.grid(row=0,column=1)
l3.grid(row=0,column=0)
l4.grid(row=1,column=2)
l1.grid(row=2,column=2)
e1.grid(row=3,column=2)
b.grid(row=4,column=2)
l4.grid(row=5,column=2)
l2.grid(row=6,column=2)
e2.grid(row=7,column=2)
i.mainloop()
#método de desconexão caso a interface seja fechada
s.shutdown(socket.SHUT_RDWR)
s.close()
