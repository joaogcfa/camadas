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
serialName = "COM4"                  # Windows(variacao de)


def main():
    try:
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        coms = enlace(serialName)
    
        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        coms.enable()
    
      
        
        imageW = "./imgs/imagem_recebido.png"
        print('peguei o diretorio da imagem a ser colada')

        resposta_head, nRx = coms.getData(128, False)
        print("-------------------------")
        print("Peguei o Handshake")
        print("-------------------------")
        pacotes = int.from_bytes(resposta_head[4:5], byteorder='big')
        pacotes_chegando = 0
        rxBuffer = bytearray()
        bytes_imagem = []
        
        #acesso aos bytes recebidos
        while pacotes_chegando < pacotes:
            print("entrou no while")
            cabecalho, nRx = coms.getData(10,False)
            print('pacotes chegando ',pacotes_chegando)
            print('cabecalho ',int.from_bytes(cabecalho[6:7], byteorder='big'))

            if int.from_bytes(cabecalho[6:7], byteorder='big') == pacotes_chegando:
                size_pay = int.from_bytes(cabecalho[2:3], byteorder='big')
                payload, nRx = coms.getData(size_pay,False)
                eop, nRx = coms.getData(4,False)

                resposta = cabecalho + payload + eop

                # palavra = "FIIM"
                # teste_eop = palavra.encode
                # print(teste_eop)

                if eop == "FIIM".encode():

                    if resposta[0:1] == int(1).to_bytes(1, byteorder = 'big'):
                        print('recepção do HandShake vai começa')
                        print('----------------------------------------')
                        print("HandShake iniciado")
                        novo_head = [2, 0, 114, 0, pacotes, 0, 0, 0, 0, 0]
                        head = bytes(novo_head)

                        pacote_hs_devolvido = head + resposta[10:128] 
                        print("pacote novo")
                        coms.sendData(pacote_hs_devolvido)
                        print("Resposta do HandShake enviado")

                    if resposta[0:1] == int(3).to_bytes(1, byteorder = 'big'):        
                        print("entrei no segundo if")
                        valor = size_pay + 10
                        # print('valor', valor)
                        teste = resposta[10:valor]
                        bytes_imagem.append(teste)
                        coms.sendData(resposta)
                        pacotes_chegando+=1
                        print(pacotes_chegando)
                    
                else:
                    print("Tamanho de payload não era igual ao informado")
                    comc.disable()
                    sys.exit(0)
            else:
                print("Pacote enviado não era o esperado")
                comc.disable()
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
