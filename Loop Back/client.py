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

        
        tamanhoImagem = len(txBuffer)/114
        resto = len(txBuffer) % 114
        

        print('RESTOOOOOO', resto)

        i = 0
        e=0
        payloadList = []

        while i < len(txBuffer)-resto:

            payload = txBuffer[i:i+114]

            payloadList.append(payload)
            print('AQUIIII')

            i += 114
            e += 1
        payload = txBuffer[i:i+resto]
        e+=1
        payloadList.append(payload)
        print("payload lista", payloadList)

        print('AUHAKJHAKJHKA', i+resto)
        print(len(payloadList))
        print("e",e)
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
        handshake = [1, 0, 114, 0, e, 0, 0, 0, 0, 0]
        head = bytes(handshake)

        head_hand_server = [2, 0, 114, 0, e, 0, 0, 0, 0, 0]
        head_server = bytes(head_hand_server)
        
        payload_hs = bytes(114)
        palavra = 'FIIM'
        eop = palavra.encode()
        print("eop", eop)
        
        def enviadados(head, payload_hs, eop):
            print("entrou na função")
            pacote = head + payload_hs[:] + eop[:]
            print("pacote", pacote)
            comc.sendData(pacote)
            time.sleep(0.5)
            comc.sendData(pacote)

#------------------------------------------
            resposta_head, nRx = comc.getData(10, True)
            resposta_pack, nRx = comc.getData(114, True)
            resposta_eop, nRx = comc.getData(4, True)

            return(resposta_head)
            
        resposta_head = enviadados(head, payload_hs, eop)
        print(resposta_head)
        print(head_server)


 
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
            head_certo = [3, 0, tamanho_payload , 0, e, 0, 0, 0, 0, 0]
            head_novo = bytes(head_certo)
            pacote_fragmentado = head_novo + payloadList[e] + eop[:]
            print('pacote a ser enviado: ', pacote_fragmentado)
            comc.sendData(pacote_fragmentado)
            
            # time.sleep(0.5)
            banana, nRx = comc.getData(tamanho_payload, False)
            if banana == payloadList[e]:
                e+=1
                print("O pacote {} foi enviado de {} pacotes".format(e,len(payloadList)))
        print(e)


        
#-------------------------------------------------------------------------------------------------------

        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # Tente entender como esse método funciona e o que ele retorna
       
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        print('recepção vai começa')
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen
      
        #acesso aos bytes recebidos


        tamanho_recebido, nRx = comc.getData(4, False)
        compara = int.from_bytes(tamanho_recebido,byteorder='big')

        if compara == len(txBuffer):
            print("recebido e enviado estão iguais")
            tempo_final = time.time()
            taxa = compara/(tempo_final-tempo_inicial)
            print(taxa)
        else:
            print("algo deu errado")


    
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
