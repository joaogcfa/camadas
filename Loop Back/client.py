####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 

from threading import Timer
import time
from enlace import *
import crcmod.predefined
from datetime import datetime
crc16_func = crcmod.predefined.mkCrcFun('crc-16')


# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
serialName = "/dev/tty.usbmodem14101" # Mac    (variacao de)
# serialName = "COM3"                  # Windows(variacao de)


def main():

    
    try:
        comc = enlace(serialName)
        comc.enable()

        txt_1 = open("Client1.txt", "w")
        txt_2 = open("Client3.txt", "w")
        # txt_3 = open("Client3.txt", "w")
        txt_4 = open("Client5.txt", "w")
        # txt_5 = open("Client5.txt", "w")

        ##Escolhendo a imagem
        pergunta = input("escolha sua imagem: ")
        imageR = './imgs/{}.png'.format(pergunta)
        txBuffer = open(imageR, 'rb').read()
        print('Imagem escolhida com sucesso!')

        
        tamanhoImagem = len(txBuffer)/114
        resto = len(txBuffer) % 114
        

        ## Verificando quantidades de pacotes
        i = 0
        total_depack=0
        payloadList = []

        while i < len(txBuffer)-resto:

            payload = txBuffer[i:i+114]

            payloadList.append(payload)

            i += 114
            total_depack += 1
        payload = txBuffer[i:i+resto]
        total_depack+=1
        payloadList.append(payload)

#------------------------------------------ setando o handshake
        #  0       1           2         3            4                      5             
        #[tipo, id sensor, id servidor,n pacotes, pacote a ser enviado, id do arquivo,
        #         6    
        # pacote solicitado pra recomeço quando há erro no envio,
        #     7                                8    9
        # ultimo pacote recebido com sucesso, CRC, CRC]

        #head do client pro server
        handshake = [1, 7, 9, total_depack, 144, 4, 0, 0, 0, 0]
        head = bytes(handshake)
         

        #head que o cliente tem que receber do server
        head_hand_server = [2, 7, 9, total_depack, 144, 4, 0, 0, 0, 0]
        head_server = bytes(head_hand_server)
        
        payload_hs = bytes(114)
        palavra = 'FIIM'
        eop = palavra.encode()
        

        #Funcao que monsta o handshake:
        def enviadados(head, payload_hs, eop):
            print("-------------------------")
            print("ENVIANDO HANDSHAKE")
            print("-------------------------")
            pacote = head + payload_hs[:] + eop[:]
            comc.sendData(pacote)
            dateTimeObj = datetime.now()
            txt_4.write(str(dateTimeObj))
            txt_4.write(" / ")
            txt_4.write("envio")
            txt_4.write(" / ")
            txt_4.write(str(int.from_bytes(head[0:1],byteorder='big')))
            txt_4.write(" / ")
            txt_4.write(str(len(pacote)))
            txt_4.write("\n")
            # time.sleep(0.5)

#------------------------------------------ pegando o handshake



            resposta_head, nRx = comc.getData(10, True, False)
            resposta_pack, nRx = comc.getData(114, True, False)
            resposta_eop, nRx = comc.getData(4, True, False)
            full_resposta = resposta_head+resposta_pack+resposta_eop
            dateTimeObj = datetime.now()
            txt_4.write(str(dateTimeObj))
            txt_4.write(" / ")
            txt_4.write("receb")
            txt_4.write(" / ")
            txt_4.write(str(int.from_bytes(resposta_head[0:1],byteorder='big')))
            txt_4.write(" / ")
            txt_4.write(str(len(full_resposta)))
            txt_4.write("\n")
            txt_4.write("\n")
            return(resposta_head)
            
        resposta_head = enviadados(head, payload_hs, eop)

        

#------------------------------------------ checando resposta do handshake

 
        while resposta_head != head_server:
            pergunta = input("Servidor inativo. Tentar novamente? S/N ")

            if pergunta == "S":
                print("Tentando novamente")
                resposta_head = enviadados(head, payload_hs, eop)
                print()
            else:
                print("comunicação encerrada!")
                comc.disable()
                sys.exit(0)


        print("comunicação bem sucedida com o server")
        print("iniciando o envio dos pacotes")
        print("------------------------------------")



#------------------------------------------ enviando os pacotes

           
        def cabo_tempo(time_max):

            time_max[0] = True
            return time_max

        
        e = 0
        

        timer2 = [False]
        timer = Timer(20, cabo_tempo, args=(timer2,))
        timer.start() 
        while e < len(payloadList):
            
            if e == 0:
                e+=1
            tamanho_payload = len(payloadList[e])  
            crcInt = crc16_func(payloadList[e])
            crc = crcInt.to_bytes(2, byteorder='big')
            # print(tamanho_payload)
            #tipo de mensagem, 0, tamanho_payload, 0, qual pacote      
            head_certo = [3, 7, 9, total_depack, e+1, tamanho_payload,0, e, 0, 0]  
            head_check = [4, 7, 9, total_depack, e+1, tamanho_payload,0, e, 0, 0]  
            head_erro = [6, 7, 9, total_depack, e+1, tamanho_payload,0, e, 0, 0]    
            head_3 = bytearray(head_certo)
            head_3[8:9] = crc[0:1] 
            head_3[9:10] = crc[1:2]
            head_4 = bytearray(head_check)
            head_4[8:9] = crc[0:1] 
            head_4[9:10] = crc[1:2]
            head_6 = bytearray(head_erro)
            head_6[8:9] = crc[0:1] 
            head_6[9:10] = crc[1:2]
            pacote_fragmentado = head_3 + payloadList[e] + eop[:]
            pacote_check = head_4 + payloadList[e] + eop[:]
            # print('LEN DE PACOTE FRAGAMENTO-----------------', len(pacote_fragmentado))
            comc.sendData(pacote_fragmentado)
            dateTimeObj = datetime.now()
            txt_4.write(str(dateTimeObj))
            txt_4.write(" / ")
            txt_4.write("envio")
            txt_4.write(" / ")
            txt_4.write(str(head_certo[0]))
            txt_4.write(" / ")
            txt_4.write(str(len(pacote_fragmentado)))
            txt_4.write(" / ")
            txt_4.write(str(e))
            txt_4.write(" / ")
            txt_4.write(str(total_depack))
            txt_4.write(" / ")
            txt_4.write(str(crc))
            txt_4.write("\n")
            print("O pacote {} foi enviado de {} pacotes".format(e,len(payloadList)))
        
            # time.sleep(0.5)
            pacote_server, nRx = comc.getData(len(pacote_fragmentado), True, False)
            dateTimeObj = datetime.now()
            txt_4.write(str(dateTimeObj))
            txt_4.write(" / ")
            txt_4.write("receb")
            txt_4.write(" / ")
            txt_4.write(str(int.from_bytes(pacote_server[0:1],byteorder='big')))
            txt_4.write(" / ")
            txt_4.write(str(len(pacote_server)))
            txt_4.write("\n")
            txt_4.write("\n")
            # print(timer2)
            # print("O QUE O CLIENT RECEBEU:",pacote_server)
            # print("O QUE O CLIENT QUERIA:",pacote_check)
            if timer2 == [False]:
                if pacote_server == pacote_check:
                    print("-------------------------")
                    print("Pacotes estão iguais")
                    if pacote_server[10:tamanho_payload+10] == pacote_check[10:tamanho_payload+10]:
                        print("Payloads estão iguais")
                        print("-------------------------")
                        timer = Timer(20, cabo_tempo, args=(timer2,))
                        timer.start()
                        e+=1
                    else: 
                        print('erro: Payloads não estavam iguais')
                        comc.disable()
                        sys.exit(0)

                # Recebendo de erro e tentando corrigi-lo
                elif pacote_server[0:1] == head_6[0:1]:
                    print("ERRO, RECEBIDO ERRO TIPO 6")
                    print("PACOTE ENVIADO NAO ERA ESPERADO PRO SERVER")
                    print("CLIENT ENVIOU: ", e)
                    e = int.from_bytes(pacote_server[7:8],byteorder='big')
                    print("SERVER QUERIA: ", e)
                    print("O pacote {} foi enviado de {} pacotes".format(e,len(payloadList)))
                    print("-------------------------")
                    head_certo = [3, 7, 9, total_depack, e+1, tamanho_payload,0, e, 0, 0]  
                    head_3 = bytearray(head_certo)
                    head_3[8:9] = crc[0:1] 
                    head_3[9:10] = crc[1:2]
                    pacote_fragmentado = head_3 + payloadList[e] + eop[:]
                    comc.sendData(pacote_fragmentado)
                    timer = Timer(20, cabo_tempo, args=(timer2,))
                    timer.start()
                    dateTimeObj = datetime.now()
                    txt_4.write(str(dateTimeObj))
                    txt_4.write(" / ")
                    txt_4.write("envio")
                    txt_4.write(" / ")
                    txt_4.write(str(head_certo[0]))
                    txt_4.write(" / ")
                    txt_4.write(str(len(pacote_fragmentado)))
                    txt_4.write(" / ")
                    txt_4.write(str(e))
                    txt_4.write(" / ")
                    txt_4.write(str(total_depack))
                    txt_4.write(" / ")
                    txt_4.write(str(crc))
                    txt_4.write("\n")
                
                elif pacote_server == "erro":
                    print("TIMER 1 EXCEDIDO")
                    comc.sendData(pacote_fragmentado)
                    dateTimeObj = datetime.now()
                    txt_4.write(str(dateTimeObj))
                    txt_4.write(" / ")
                    txt_4.write("envio")
                    txt_4.write(" / ")
                    txt_4.write(str(int.from_bytes(pacote_fragmentado[0:1],byteorder='big')))
                    txt_4.write(" / ")
                    txt_4.write(str(len(pacote_fragmentado)))
                    txt_4.write(" / ")
                    txt_4.write(str(e))
                    txt_4.write(" / ")
                    txt_4.write(str(total_depack))
                    txt_4.write(" / ")
                    txt_4.write(str(crc))
                    txt_4.write("\n")                    



            #TIMER2 EXCEDIDO ---------- TIMED OUT
            else:
                print("-----------TIMED OUT----------")
                print("ERRO, ENVIANDO MENSAGEM TIPO 5")
                head_timeout = [5, 7, 9, total_depack, e+1, tamanho_payload,0, e, 0, 0]
                head_5 = bytearray(head_timeout)
                head_5[8:9] = crc[0:1] 
                head_5[9:10] = crc[1:2]
                payload_timeout = bytes(114)
                pacote_timeout = head_timeout + payload_timeout[:] + eop[:]
                comc.sendData(pacote_timeout)
                dateTimeObj = datetime.now()
                txt_4.write(str(dateTimeObj))
                txt_4.write(" / ")
                txt_4.write("receb")
                txt_4.write(" / ")
                txt_4.write(str(int.from_bytes(pacote_server[0:1],byteorder='big')))
                txt_4.write(" / ")
                txt_4.write(str(len(pacote_server)))
                txt_4.write("\n")
                txt_4.write("\n")
                comc.disable()
                sys.exit(0)
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        comc.disable()
        txt_1.close()
        txt_2.close()
        # txt_3.close()
        txt_4.close()
        # txt_5.close()
    except:
        print("ops! :-\\")
        comc.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
