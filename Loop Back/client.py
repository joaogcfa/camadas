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
serialName = "/dev/tty.usbmodem14101" # Mac    (variacao de)
# serialName = "COM1"                  # Windows(variacao de)


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
        payloadList = []

        while i < len(txBuffer)-resto:

            payload = txBuffer[i:i+114]

            payloadList.append(payload)
            print('AQUIIII')

            i += 114
        payload = txBuffer[i:i+resto]
        payloadList.append(payload)

        print('AUHAKJHAKJHKA', i+resto)
        print(len(payloadList))
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são uma lista de bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.
        

        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.        
        #finalmente vamos transmitir os tados. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #tente entender como o método send funciona!
        print('vai começa o envio')
        comc.sendData(tamanho_texto)
        time.sleep(0.5)
        comc.sendData(txBuffer)

        
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


        tamanho_recebido, nRx = comc.getData(4)
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
