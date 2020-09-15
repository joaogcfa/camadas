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
        print('peguei a imageW')

        resposta_head, nRx = coms.getData(128, True)
        print(resposta_head)
        len_pack = int.from_bytes(resposta_head[2:3], byteorder='big')
        print('len_pack', len_pack)
        pacotes = int.from_bytes(resposta_head[4:5], byteorder='big')
        print('pacotes', pacotes)
        pacotes_chegando = 0
        rxBuffer = None
        bytes_imagem = []
        
        #acesso aos bytes recebidos
        while pacotes_chegando < pacotes:
            print("entrou no while")
            
            tamanho_pacote = 10 + len_pack + 4 
            print(tamanho_pacote)
            resposta, nRx = coms.getData(tamanho_pacote, False)
            len_pack = int.from_bytes(resposta_head[2:3], byteorder='big')
                
            
            if resposta[0:1] == int(1).to_bytes(1, byteorder = 'big'):
                print('recepção do HandShake vai começa')
                print('----------------------------------------')
                print("HandShake iniciado")
                novo_head = [2, 0, 114, 0, pacotes, 0, 0, 0, 0, 0]
                head = bytes(novo_head)
                print(head)

                pacote_hs_devolvido = head + resposta[10:128] 
                print("pacote novo")
                print(pacote_hs_devolvido)
                coms.sendData(pacote_hs_devolvido)
                print("Resposta do HandShake enviado")

            if resposta[0:1] == int(3).to_bytes(1, byteorder = 'big'):        
                print("entrei no segundo if")
                valor = len_pack + 10
                # print('valor', valor)
                teste = resposta[10:valor]
                bytes_imagem.append(teste)
                print("lista", bytes_imagem)
                coms.sendData(teste)
                # testeee = int.from_bytes(teste, byteorder="big")
                # print(testeee)
                # rxBuffer += testeee
                # print('rx buffer',rxBuffer)
                # pacotes_chegando+=1
                # print("Pacote {} recebido".format(pacotes_chegando))






        # tamanho1 = int.from_bytes(tamanho, byteorder='big')
        # print(tamanho1)


        # rxBuffer, nRx = coms.getData(tamanho1)
        
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
