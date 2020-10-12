####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
from threading import Timer
import crcmod.predefined
from datetime import datetime
crc16_func = crcmod.predefined.mkCrcFun('crc-16')
import time



# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "/dev/tty.usbmodem14201" # Mac    (variacao de)
# serialName = "COM4"                  # Windows(variacao de)


def main():
    try:
        txt_1 = open("Server3.txt", "w")
        # txt_2 = open("Server2.txt", "w")
        # txt_3 = open("Server3.txt", "w")
        txt_4 = open("Server4.txt", "w")
        # txt_5 = open("Server5.txt", "w")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        coms = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        coms.enable()
    
      
        
        imageW = "./imgs/imagem_recebido.png"
        print('peguei o diretorio da imagem a ser colada')

        rxBuffer = bytearray()
        bytes_imagem = []
        cont_server = 0
        ocioso = True
        while ocioso:

            resposta_hand, nRx = coms.getData(128, False, False)
            print("-------------------------")
            print("Peguei o Handshake")
            print("-------------------------")
            if resposta_hand[0:1] == int(1).to_bytes(1, byteorder = 'big'):
                if resposta_hand[2:3] == int(9).to_bytes(1, byteorder = 'big'):
                    ocioso = False
                    dateTimeObj = datetime.now()
                    txt_4.write(str(dateTimeObj))
                    txt_4.write(" / ")
                    txt_4.write("receb")
                    txt_4.write(" / ")
                    txt_4.write(str(int.from_bytes(resposta_hand[0:1],byteorder='big')))
                    txt_4.write(" / ")
                    txt_4.write(str(len(resposta_hand)))
                    txt_4.write("\n")

            time.sleep(0.1)

    
        total_depack = int.from_bytes(resposta_hand[3:4], byteorder='big')
        novo_head = [2, 7, 9, total_depack, 144, 4, 0, 0, 0, 0]
        head = bytes(novo_head)

        pacote_hs_devolvido = head + resposta_hand[10:128] 
        coms.sendData(pacote_hs_devolvido)
        print("Resposta do HandShake enviado")
        txt_4.write(str(dateTimeObj))
        txt_4.write(" / ")
        txt_4.write("envio")
        txt_4.write(" / ")
        txt_4.write(str(novo_head[0]))
        txt_4.write(" / ")
        txt_4.write(str(len(pacote_hs_devolvido)))
        txt_4.write("\n")
        txt_4.write("\n")


        def cabo_tempo(time_max):

            time_max[0] = True
            return time_max
        
        timer2 = [False]
        timer = Timer(20, cabo_tempo, args=(timer2,))
        timer.start() 

        #acesso aos bytes recebidos

        
        while cont_server < total_depack:
            print("-------------------------")
            print("ENTROU NO WHILE PRINCIPAL")
            print(timer2)

            if timer2== [False]:
                cabecalho, nRx = coms.getData(10,False, True)
                if cabecalho != "erro":
                    print("RECEBI O PACOTE")
                    size_pay = int.from_bytes(cabecalho[5:6], byteorder='big')
                    tipo = int.from_bytes(cabecalho[0:1], byteorder='big')
                    contador_client = int.from_bytes(cabecalho[7:8], byteorder='big')



                    
                    payload, nRx = coms.getData(size_pay,False, True)
                    eop, nRx = coms.getData(4,False, True)
                    if payload == "erro" or eop == "error":
                        payload = 0
                        eop = 0

                    crcInt = crc16_func(payload)
                    crc = crcInt.to_bytes(2, byteorder='big')

                    
                    resposta = cabecalho + payload + eop

                    dateTimeObj = datetime.now()

                    txt_4.write(str(dateTimeObj))
                    txt_4.write(" / ")
                    txt_4.write("receb")
                    txt_4.write(" / ")
                    txt_4.write(str(tipo))
                    txt_4.write(" / ")
                    txt_4.write(str(len(resposta)))
                    txt_4.write(" / ")
                    txt_4.write(str(contador_client))
                    txt_4.write(" / ")
                    txt_4.write(str(total_depack))
                    txt_4.write(" / ")
                    txt_4.write(str(crc))
                    txt_4.write("\n")
                                

                    if tipo == 3:
                        if eop == "FIIM".encode():
                            if contador_client == cont_server:
                                print("TUDO CERTO")
                                novo_head = [4, 7, 9, total_depack, cont_server+1, size_pay,0, cont_server, 0, 0]
                                head_4 = bytearray(novo_head)
                                head_4[8:9] = crc[0:1] 
                                head_4[9:10] = crc[1:2]
                                pacote_resposta =  head_4 + payload[:] + eop[:]       
                                valor = size_pay + 10
                                # print('valor', valor)
                                teste = resposta[10:valor]
                                bytes_imagem.append(teste)
                                coms.sendData(pacote_resposta)
                                cont_server+=1
                                timer = Timer(20, cabo_tempo, args=(timer2,))
                                timer.start()
                                dateTimeObj = datetime.now()
                                txt_4.write(str(dateTimeObj))
                                txt_4.write(" / ")
                                txt_4.write("envio")
                                txt_4.write(" / ")
                                txt_4.write(str(head_4[0]))
                                txt_4.write(" / ")
                                txt_4.write(str(len(pacote_resposta)))
                                txt_4.write("\n")
                                txt_4.write("\n")
                                print("-------------------------")

                            
                            else:
                                print("CONTADOR CLIENT: ", contador_client)
                                print("CONTADOR SERVER: ", cont_server)
                                head_erro = [6, 7, 9, total_depack, cont_server+1, size_pay,0, cont_server, 0, 0]
                                head_6 = bytes(head_erro)
                                pacote_erro = head_6 + payload + eop
                                print("Pacote enviado não era o esperado")
                                print("ENVIANDO PACOTE NUMERO: ", cont_server)
                                coms.sendData(pacote_erro)
                                dateTimeObj = datetime.now()
                                txt_4.write(str(dateTimeObj))
                                txt_4.write(" / ")
                                txt_4.write("envio")
                                txt_4.write(" / ")
                                txt_4.write(str(head_6[0]))
                                txt_4.write(" / ")
                                txt_4.write(str(len(pacote_erro)))
                                txt_4.write("\n")
                                txt_4.write("\n")
                                print("-------------------------")

                        else:
                            head_erro = [6, 7, 9, total_depack, cont_server+1, size_pay,0, cont_server, 0, 0]
                            head_6 = bytes(head_erro)
                            pacote_erro = head_6 + payload + eop
                            print("Tamanho de payload não era igual ao informado")
                            print("ENVIANDO PACOTE NUMERO: ", cont_server)
                            coms.sendData(pacote_erro)
                            dateTimeObj = datetime.now()
                            txt_4.write(str(dateTimeObj))
                            txt_4.write(" / ")
                            txt_4.write("envio")
                            txt_4.write(" / ")
                            txt_4.write(str(head_6[0]))
                            txt_4.write(" / ")
                            txt_4.write(str(len(pacote_erro)))
                            txt_4.write("\n")
                            txt_4.write("\n")
                            print("-------------------------")
                                
                else:
                    print("Timer 1 excedido")
                    novo_head = [4, 7, 9, total_depack, cont_server+1, size_pay,0, cont_server, 0, 0]
                    head_4 = bytes(novo_head)
                    coms.sendData(pacote_resposta)
                    dateTimeObj = datetime.now()
                    txt_4.write(str(dateTimeObj))
                    txt_4.write(" / ")
                    txt_4.write("envio")
                    txt_4.write(" / ")
                    txt_4.write(str(head_4[0]))
                    txt_4.write(" / ")
                    txt_4.write(str(len(pacote_resposta)))
                    txt_4.write("\n")
                    txt_4.write("\n")
                    print("-------------------------")
            else:
                print("-----------TIMED OUT----------")
                print("ERRO, ENVIANDO MENSAGEM TIPO 5")
                ocioso = True
                head_pre_timeout = [5, 7, 9, 0, 0, 0,0, 0, 0, 0]
                eop = "FIIM".encode()
                head_timeout = bytes(head_pre_timeout)
                payload_timeout = bytes(114)
                pacote_timeout = head_timeout + payload_timeout[:] + eop
                coms.sendData(pacote_timeout)
                dateTimeObj = datetime.now()
                txt_4.write(str(dateTimeObj))
                txt_4.write(" / ")
                txt_4.write("envio")
                txt_4.write(" / ")
                txt_4.write(str(head_pre_timeout[0]))
                txt_4.write(" / ")
                txt_4.write(str(len(pacote_timeout)))
                txt_4.write("\n")
                txt_4.write("\n")
                coms.disable()
                sys.exit(0)




            




        for e in bytes_imagem:
            rxBuffer += e

        
        

        time.sleep(0.1)
        tamanho_rx_recebido = (int(len(rxBuffer))).to_bytes(4,byteorder = 'big')
        coms.sendData(tamanho_rx_recebido)
    
    
        print('salvando dados no arquivo')
        f = open(imageW,'wb')
        f.write(rxBuffer)
        f.close()
        txt_1.close()
        # txt_2.close()
        # txt_3.close()
        txt_4.close()
        # txt_5.close()

    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        coms.disable()
    except:
        coms = enlace(serialName)
        print("ops! :-\\")
        coms.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
