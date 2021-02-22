import socket
import threading      #biblioteca para criação e execução de threads simultâneas
import time
import tkinter as tk  #biblioteca para criação de interfaces
import struct

host=0
port=0
port_ext=0

Eleicao=False
Lider=False
Loop=True

sv1=''
sv2=''
sv3=''

so=socket.socket()
so_ext=socket.socket()

cur_unix_time=lambda:int(time.time()*10000000)
token=cur_unix_time()

#224.0.0.0 - 225.0.0.0
multicast_group='224.0.0.0' #ip para multicast selecionado dentro do intervalo permitido
# print(token)
conexoes=[]
enderecos=[]

def configura_socket():
  global so
  criar_socket()
  bindar_socket()
  recebe_mensagem()

def configura_socket_ext():
    global so_ext,Lider,Eleicao
    while(Loop):
      if(Lider and not Eleicao):
        criar_socket_ext()
        bindar_socket_ext()
        aceit_conexoes_ext()

def criar_socket():
  try:
    global host,port,so
    host=str(socket.gethostbyname(socket.gethostname()))
    # 0<port<10000
    port=9999
    so=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  except socket.error as msg:
    print('erro na criacao de socket: '+str(msg))

def criar_socket_ext():
  try:
    global host,port_ext,so_ext
    host=str(socket.gethostbyname(socket.gethostname()))
    port_ext=9998
    so_ext=socket.socket()
  except socket.error as msg:
    print('erro na criacao de socket externo: '+str(msg))

def bindar_socket():
  global host
  try:
    global so
    print('porta '+str(port)+' bindada'+'\n')
    so.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print(host,port)
    so.bind((host, port))
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    so.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    so.settimeout(1)
  except socket.error as msg:
    print('erro ao bindar o socket: '+str(msg))
    bindar_socket()

def bindar_socket_ext():
  try:
    global so_ext
    print('porta '+str(port_ext)+' bindada externamente')
    so_ext.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    so_ext.bind((host, port_ext))
    so_ext.listen(5)
    so_ext.settimeout(1)
  except socket.error as msg:
    print('erro ao bindar o socket externo: '+str(msg))
    bindar_socket_ext()

def recebe_mensagem():
  global Eleicao,Lider,sv3,sv2
  q=0
  while(Loop):
    try:
      data = so.recv(20480)
      print(data)
      if(data and not Eleicao):
        if(Lider and data != b'Lid_ok'):
          manda_mensagem('Lid_ok')
        if(data.decode("utf-8").startswith('I2E_')):
          if(Lider):
            for c in conexoes:
              c.send(data.decode("utf-8")[4:].encode())
        elif(data.decode("utf-8").startswith('Ele_')):
          Eleicao=True
        elif(not(data.decode("utf-8").startswith('Lid_')) and not(data.decode("utf-8").startswith('Tok_'))):#mensagens em geral 
          sv2.set(data.decode("utf-8"))
        print(data)
      else:
        a=int(data.decode("utf-8")[4:])
        if(a!=token and Lider):
          if(a<token):
            Lider=False
            sv3.set(str(Lider))
            Eleicao=False
        else:
          q=q+1
        if(q>3):
          Eleicao=False
      data=''
    except:
      continue
  print('receive_message fechado\n')

def recebe_mensagem_ext():
  global so,so_ext
  global Lider,Loop
  global conexoes

  while(Loop):
    if(Lider and not Eleicao):
      for cn in conexoes:
        try:
          cn.settimeout(1)
          data2 = cn.recv(20480)
          if(data2 and data2.decode("utf-8")!=' '):
            print(data2)
            manda_mensagem(data2.decode("utf-8")[4:])
          data2=''
        except:
          continue

def fechar_conexoes():
  global conexoes,enderecos
  for c in conexoes:
    c.shutdown(socket.SHUT_RDWR)
    c.close()

  del conexoes[:]
  del enderecos[:]

def aceit_conexoes_ext():
  global Lider,Eleicao
  fechar_conexoes() #evitar conexões fantasma que impedem comunicação externa
  while(Loop):
    try:
      conex,ender=so_ext.accept()
      so_ext.setblocking(1)

      conexoes.append(conex)
      enderecos.append(ender)

      print('Conexao estabelecida com: '+str(ender[0]))
      print('Enderecos conectados: \n'+str(enderecos))
    except:
      print('Busca falhou, buscando novamente...')

def vivo():
  global enderecos,conexoes
  while(Loop):
    if Lider and not Eleicao:
      time.sleep(1)
      for i,conex in enumerate(conexoes):
        try:
          conex.send(' '.encode())
        except:
          del conexoes[i]
          print('Conexao com '+str(enderecos[i])+' perdida')

          del enderecos[i]
          print('Enderecos conectados: \n'+str(enderecos))
          continue

def manda_mensagem(msg):
  grupo=(multicast_group,port)
  so_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  so_envio.settimeout(0.2)
  ttl = struct.pack('b', 1)

  so_envio.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
  so_envio.sendto(msg.encode(),grupo)

def pega_mensagem():
  #pega da interface ou linha de comando
  global Eleicao,sv1
  msg=sv1.get()
  manda_mensagem(msg)
  def elec_or_n():
    global Eleicao
    if(not(Eleicao)):
      i=0
      while(i<5): #
        try:
          data=so.recv(20480) #limite de bytes enviados/recebidos
          if(data and data.decode("utf-8").startswith('Lid_')):
            i=6
          i+=1
        except:
          i+=1
          continue  
      if(i==5):
        Eleicao=True
  te = threading.Thread(target=elec_or_n,daemon=True)
  te.start()


def pega_mensagem_ext():
   global sv1
   msg=sv1.get()
   manda_mensagem('I2E_'+msg)

def eleicao():
  global Lider,sv3,Eleicao
  while(Loop):
    if(Eleicao):
      manda_mensagem('Ele_now')
      Lider=True
      sv3.set(str(Lider))
      while(Eleicao):#identificacao de lider
        manda_mensagem('Tok_'+str(token))

i=tk.Tk()

sv1=tk.StringVar()
sv2=tk.StringVar()
sv3=tk.StringVar()

sv3.set(str(Lider))

b1=tk.Button(i,text='manda mensagem mult',command=pega_mensagem)
b2=tk.Button(i,text='manda mensagem ext',command=pega_mensagem_ext)

l1=tk.Label(text='ENVIO')
l2=tk.Label(text='RECEBIMENTO')
l3=tk.Label(text='Lider')

l4=tk.Label(i,text='')
l5=tk.Label(i,text='')

e1=tk.Entry(i,textvariable=sv1,width=20)
e2=tk.Entry(i,textvariable=sv2,width=20)
e3=tk.Entry(i,textvariable=sv3,width=5)

#thread para configuração do socket interno do multicast
t1 = threading.Thread(target=configura_socket,daemon=True)
t1.start()

#thread para ping do lider
t2 = threading.Thread(target=eleicao,daemon=True)
t2.start()

#thread para configuração do socket externo no processo líder
t3 = threading.Thread(target=configura_socket_ext,daemon=True)
t3.start()

#thread para verificação de processo externos ativos
t4 = threading.Thread(target=vivo,daemon=True)
t4.start()

#thread para recebimento de mensagens externas ao multicast pelo lider
t5 = threading.Thread(target=recebe_mensagem_ext,daemon=True)
t5.start()

#1 - criar socket interno
#2 - eleicao
#3 - criar socket externo
#4 - vivo
#5 - receber mensagem externa

#INICIO INTERFACE



i.geometry('475x200')

l3.grid(row=0,column=0)
e3.grid(row=0,column=1)

l4.grid(row=1,column=0)

l1.grid(row=2,column=0)
e1.grid(row=2,column=1)

b1.grid(row=3,column=0)
b2.grid(row=3,column=1)

l5.grid(row=4,column=0)

l2.grid(row=5,column=0)
e2.grid(row=5,column=1)

i.mainloop()

Loop=False
fechar_conexoes()
time.sleep(0.5)

so.close()
so_ext.close()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
