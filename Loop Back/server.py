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
# serialName = "/dev/tty.usbmodem14201" # Mac    (variacao de)
serialName = "C4M"                  # Windows(variacao de)


def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        coms = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        coms.enable()
    
      
        print('recepção vai começa')
        #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        #Veja o que faz a funcao do enlaceRX  getBufferLen

        imageW = "./imgs/imagem_recebido.png"
        print(imageW)
        #acesso aos bytes recebidos
        time.sleep(0.5)
        tamanho, nRx = coms.getData(4)
        print(tamanho)

        tamanho1 = int.from_bytes(tamanho, byteorder='big')
        print(tamanho1)


        rxBuffer, nRx = coms.getData(tamanho1)
        print('rxBuffer')

        time.sleep(0.1)
        tamanho_rx_recebido = (int(len(rxBuffer))).to_bytes(4,byteorder = 'big')
        coms.sendData(tamanho_rx_recebido)
    
    
        print('salvando dados no arquivo')
        f = open(imageW,'wb')
        f.write(rxBuffer)
        f.close()
    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        coms.disable()
    except:
        print("ops! :-\\")
        coms.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
