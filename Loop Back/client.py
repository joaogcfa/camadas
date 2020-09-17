####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time


# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
# serialName = "/dev/tty.usbmodem14101" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)


def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        comc = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        comc.enable()

        
        pergunta = input("escolha sua imagem: ")
        imageR = './imgs/{}.png'.format(pergunta)
        txBuffer = open(imageR, 'rb').read()
        print('Imagem escolhida com sucesso!')

        


        tamanhoImagem = len(txBuffer)/114
        resto = len(txBuffer) % 114
        


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

        # tamanho_payload = len(payloadList[e])
        # print("tamanho payload", tamanho_payload)
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        

        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.        
        #finalmente vamos transmitir os tados. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        #[tipo, 0, quantidade de bytes, 0, numero do pacote,0,0,0,0,0 ]
        handshake = [1, 0, 114, 0, total_depack, 0, 0, 0, 0, 0]
        head = bytes(handshake)

        head_hand_server = [2, 0, 114, 0, total_depack, 0, 0, 0, 0, 0]
        head_server = bytes(head_hand_server)
        
        payload_hs = bytes(114)
        palavra = 'FIIM'
        eop = palavra.encode()
        
        def enviadados(head, payload_hs, eop):
            print("-------------------------")
            print("ENVIANDO HANDSHAKE")
            print("-------------------------")
            pacote = head + payload_hs[:] + eop[:]
            comc.sendData(pacote)
            time.sleep(0.5)
            comc.sendData(pacote)

#------------------------------------------
            resposta_head, nRx = comc.getData(10, True)
            resposta_pack, nRx = comc.getData(114, True)
            resposta_eop, nRx = comc.getData(4, True)

            return(resposta_head)
            
        resposta_head = enviadados(head, payload_hs, eop)


 
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


        e = 0
        while e < len(payloadList):
            tamanho_payload = len(payloadList[e])  
            print(tamanho_payload)
            #tipo de mensagem, 0, tamanho_payload, 0, qual pacote      
            head_certo = [3, 0, tamanho_payload , 0, total_depack, 0, e, 0, 0, 0]
            head_novo = bytes(head_certo)
            pacote_fragmentado = head_novo + payloadList[e] + eop[:]
            # print('LEN DE PACOTE FRAGAMENTO-----------------', len(pacote_fragmentado))
            comc.sendData(pacote_fragmentado)
            print("O pacote {} foi enviado de {} pacotes".format(e,len(payloadList)))
            
            # if e == 0:
            #     e+=1
            print(e)



            # time.sleep(0.5)
            pacote_server, nRx = comc.getData(len(pacote_fragmentado), True)
            if pacote_server == pacote_fragmentado:
                print("-------------------------")
                print("Pacotes estão iguais")
                print("-------------------------")
                if pacote_server[10:tamanho_payload+10] == pacote_fragmentado[10:tamanho_payload+10]:
                    print("-------------------------")
                    print("Payloads estão iguais")
                    print("-------------------------")
                    e+=1
                else: 
                    print('erro: Payloads não estavam iguais')
                    comc.disable()
                    sys.exit(0)
            else:
                print('erro: Pacotes não estavam iguais')
                comc.disable()
                sys.exit(0)
        


    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        comc.disable()
    except:
        print("ops! :-\\")
        comc.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
