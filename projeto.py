import sys, os
import tarfile
import math
import time
import matplotlib.pyplot as plt

from bitarray import bitarray, frozenbitarray
from bitarray.util import int2ba, ba2int, strip

def string_tamanho(n_bit):
    tamanho = ""
    if n_bit >= 8 * 1024:
        tamanho = f"{int(n_bit) / (8 * 1024)} kB"
    elif n_bit >= 8 * 1024 * 1024:
        tamanho = f"{int(n_bit) / (8 * 1024 * 1024)} MB"
    elif n_bit >= 8:
        tamanho = f"{int(n_bit) / 8} B"
    else:
        tamanho= f"{int(n_bit)} b"
    return tamanho

def calc_comprimento_medio(n_bit,n_symbol):
    return n_bit/n_symbol

def cal_entropia(dict_cont, n_symbol):
    entropia = 0
    for key_s in dict_cont:
        #print("N: ",n_symbol,"key: ", key_s, "dict_cont[key]:", dict_cont[key_s])
        entropia += (dict_cont[key_s]/n_symbol) * math.log(n_symbol/dict_cont[key_s], 2)
    return entropia
    

def initialize_dictionary_encode():
    return {bytes([i]): frozenbitarray(int2ba(i+1)) for i in range(256)}

#comprimento médio = numero de bits / simbolos codificados
#entropia = somatorio das informações
#informação = log 1/p
#tempo de compressão e descompressão
def encode(data, dictionary, file, p, static_dictionary, rc):
    n_symbol = 0
    n_bits = 0
    tam_result = 0
    tam_input = 0
    graph_tam_symbol_x = []
    graph_tam_symbol_y = []
    cont_100_mais = False
    posicao_100 = 0
    flag_estatico_por_rc = False
    posicao_delta = 0
    dict_cont_s = {}
    bits_to_write = 64
    b = 9
    cont = 0
    buffer = b'' # ultima frase encontrada no dicionario
    result = bitarray()
    with open(file, 'wb') as write_file:
        for symbol in data: #
            n_symbol += 1
            new_buffer = buffer + bytes([symbol]) 
            
            #cont de simbolos
            if bytes([symbol])  in dict_cont_s:
                dict_cont_s[bytes([symbol])] += 1
            else:
                dict_cont_s[bytes([symbol])] = 1

            if new_buffer in dictionary: 
                buffer = new_buffer 
            else: # quebrou a coincidência 
                
                tamanho_buffer = len(dictionary[buffer])
                
                if(tamanho_buffer < b):
                    result = result + bitarray(b - tamanho_buffer)

                result = result + dictionary[buffer]
                tam_result += b
                tam_input += len(buffer)
                graph_tam_symbol_x.append(tam_input)
                graph_tam_symbol_y.append(tam_result / tam_input)

                #print('Bits por simbolo:', dictionary[buffer])
                #print(result, "int: ", ba2int(dictionary[buffer]), "b:", b, "simbolo: ", buffer, "\n")
                tamanho_dict = len(dictionary)
                
                if(rc and tamanho_dict >= p and not cont_100_mais and not flag_estatico_por_rc):
                    posicao_100 = len(graph_tam_symbol_y)
                    cont_100_mais = True
                
                if tamanho_dict < p or (cont_100_mais and not flag_estatico_por_rc):
                    dictionary[new_buffer] = frozenbitarray(int2ba(tamanho_dict+1))
                    newTamanho = len(dictionary[new_buffer])
                    if(newTamanho > b):
                        b = newTamanho
                    if(cont_100_mais and len(graph_tam_symbol_y) == posicao_100+100):
                        cont_100_mais = False
                        flag_estatico_por_rc = True

                elif rc and (posicao_delta == 0 or posicao_delta+100 == len(graph_tam_symbol_y)): 
                    delta_l =  graph_tam_symbol_y[len(graph_tam_symbol_y)-1] / graph_tam_symbol_y[len(graph_tam_symbol_y)-200]
                   
                    if(delta_l >= 1.1): #rc decrescente
                        print(delta_l)
                        flag_estatico_por_rc = False
                        cont_100_mais = False
                        b = 9
                        dictionary = initialize_dictionary_encode()
                        tamanho_dict = len(dictionary)
                        dictionary[new_buffer] = frozenbitarray(int2ba(tamanho_dict+1))
                        posicao_delta = 0

                    else:
                        posicao_delta = len(graph_tam_symbol_y) #480
                        flag_estatico_por_rc = True
                        cont_100_mais = True
                    
                elif not rc and not static_dictionary:
                    b = 9
                    dictionary = initialize_dictionary_encode()
                    tamanho_dict = len(dictionary)
                    dictionary[new_buffer] = frozenbitarray(int2ba(tamanho_dict+1))
                    #print('Clear D', new_buffer, bytes([symbol]))
                    #dictionary[bytes([symbol])] = frozenbitarray(int2ba(tamanho_dict))

                buffer = bytes([symbol])
                 
                #if b > bits_to_write:
                #    bits_to_write = bits_to_write + 8
                if len(result) >= bits_to_write:
                    times_to_write = int(len(result) / bits_to_write)
                    #print('Simbolos: ', result[:(bits_to_write * times_to_write)])
                    n_bits += len(result[:(bits_to_write * times_to_write)])
                    write_file.write(result[:(bits_to_write * times_to_write)])
                    result = result[(bits_to_write * times_to_write):]
                
        if buffer:
            tamanho = len(dictionary[buffer])
            if(tamanho < b):
                result = result + bitarray(b - tamanho)
            result = result + dictionary[buffer]
            tam_result += b
            tam_input += len(buffer)
            graph_tam_symbol_x.append(tam_input)
            graph_tam_symbol_y.append(tam_result / tam_input)
            #print('Simbolos: ', result)
            n_bits += len(result)
            #print(result, "int: ", ba2int(dictionary[buffer]), "b:", b, "simbolo: ", buffer, "\n")
        result = result + bitarray(b)
        write_file.write(result)
        
        #print ("Tamanho: ", string_tamanho(n_bits))
        print ("Comprimento médio:", calc_comprimento_medio(n_bits,n_symbol))
        print ("Entropia: ", cal_entropia(dict_cont_s,n_symbol))
        # Criando o gráfico
        """ plt.plot(graph_tam_symbol_x, graph_tam_symbol_y)
        plt.xscale('log')
        # Adicionando rótulos e título
        plt.xlabel('Eixo X')
        plt.ylabel('Eixo Y')
        plt.title('Gráfico de Linha Simples')
        plt.show() """


def lzw_compress(data, file, p, static_dictionary=False, rc=False):
    dictionary = initialize_dictionary_encode()
    #print("Dicionário inicial:", dictionary)
    encode(data, dictionary, file, p, static_dictionary, rc)
    #print(dictionary)

def initialize_dictionary_decode():
    return {frozenbitarray(int2ba(i+1)): bytes([i]) for i in range(256)}

def decode(data, dictionary, file, p, static_dictionary, rc):
    data_len = len(data)
    b = 9
    buffer = b'' # 
    result = b''
    tam_result = 0
    tam_input = 0
    graph_tam_symbol_x = []
    graph_tam_symbol_y = []
    cont_100_mais = False
    posicao_100 = 0
    flag_estatico_por_rc = False
    posicao_delta = 0
    cur_index = 0
    cont = 0
    with open(file, 'wb') as write_file:
        while True: #
            dict_len = len(dictionary)

            if(rc and dict_len >= p and not cont_100_mais and not flag_estatico_por_rc):
                posicao_100 = len(graph_tam_symbol_y)
                cont_100_mais = True

            aumenta_dicionario = dict_len < p or (cont_100_mais and not flag_estatico_por_rc)
            mede_delta_l = not aumenta_dicionario and (rc and (posicao_delta == 0 or posicao_delta+100 == len(graph_tam_symbol_y)))
            reseta_rc = mede_delta_l and graph_tam_symbol_y[len(graph_tam_symbol_y)-1] / graph_tam_symbol_y[len(graph_tam_symbol_y)-200] >= 1.1
            reseta_dicionario = not static_dictionary and dict_len >=p and (not rc or reseta_rc)

            if reseta_dicionario:
                b = 9
            symbol = strip(data[cur_index:b+cur_index], mode="left") #2
            if(len(symbol) == 0):
                break
            cur_index = cur_index + b
            tam_result += b

            #if len(symbol) < 8:
            #    symbol = bitarray(8 - len(symbol)) + symbol

            frozen_symbol = frozenbitarray(symbol)

            if aumenta_dicionario:
                if buffer:
                    if frozen_symbol not in dictionary:
                        dictionary[frozenbitarray(int2ba(dict_len+1))] = buffer + bytes([buffer[0]])
                    else:
                        dictionary[frozenbitarray(int2ba(dict_len+1))] = buffer + bytes([dictionary[frozen_symbol][0]]) 

                if 2 ** b <= (len(dictionary)+1) and (not static_dictionary or len(dictionary) < p):
                    b = b + 1 #6
                if(cont_100_mais and len(graph_tam_symbol_y) == posicao_100+100):
                        cont_100_mais = False
                        flag_estatico_por_rc = True
            elif mede_delta_l: 
                    delta_l = graph_tam_symbol_y[len(graph_tam_symbol_y)-1] / graph_tam_symbol_y[len(graph_tam_symbol_y)-200]

                    if(delta_l >= 1.1): #rc decrescente
                        print(delta_l)
                        flag_estatico_por_rc = False
                        cont_100_mais = False
                        dictionary = initialize_dictionary_decode()
                        if buffer:
                            dict_len = len(dictionary)
                            if frozen_symbol not in dictionary:
                                dictionary[frozenbitarray(int2ba(dict_len+1))] = buffer + bytes([buffer[0]]) 
                            else:
                                dictionary[frozenbitarray(int2ba(dict_len+1))] = buffer + bytes([dictionary[frozen_symbol][0]]) 
                        posicao_delta = 0
                    else:
                        posicao_delta = len(graph_tam_symbol_y) #480
                        flag_estatico_por_rc = True
                        cont_100_mais = True
            elif not rc and not static_dictionary:
                dictionary = initialize_dictionary_decode()
                if buffer:
                    dict_len = len(dictionary)
                    if frozen_symbol not in dictionary:
                        dictionary[frozenbitarray(int2ba(dict_len+1))] = buffer + bytes([buffer[0]]) 
                    else:
                        dictionary[frozenbitarray(int2ba(dict_len+1))] = buffer + bytes([dictionary[frozen_symbol][0]]) 
                    
                #dictionary[frozenbitarray(int2ba(dict_len))] = bytes([symbol_clear]) 
            #print(result, "int: ", ba2int(symbol), "b:", b, "simbolo: ", dictionary[frozenbitarray(symbol)], "\n")
           
            result = result + dictionary[frozen_symbol] #a,a,b,ab,aba, aa
            tam_input += len(dictionary[frozen_symbol] )
            graph_tam_symbol_x.append(tam_input)
            graph_tam_symbol_y.append(tam_result / tam_input)

            buffer = dictionary[frozen_symbol]  #aa

            if(len(result) >= 2 ** 12):
                write_file.write(result)
                result = b''

            if cur_index >= data_len:
                break

        if result:
            write_file.write(result)

def lzw_decompress(data, file, p, static_dictionary=False, rc=False):
    dictionary = initialize_dictionary_decode()
    decode(data, dictionary, file, p, static_dictionary, rc)

estatico = True
rc = False

p = 2 ** 12
#p = 2 ** 15
#p = 2 ** 18
#p = 2 ** 21

file = sys.argv[1]
file_to_open = file

filename = os.path.splitext(os.path.basename(file))[0]
original_filename = filename + os.path.splitext(os.path.basename(file))[1]

if(os.path.isdir(file)):
    filename = os.path.basename(os.path.normpath(file))
    original_filename = filename + ".tar"
    file_to_open = os.path.dirname(file) + ".tar"
    with tarfile.open(filename+".tar", 'w') as tar:
        tar.add(filename, arcname="decompressed_"+filename)

fin = open(file_to_open, "rb")

original_data = fin.read()
#print(original_data, "\n")
fin.close()

filename = f"compressed_{filename}.bin"  # Substitua "seu_arquivo.bin" pelo nome do seu arquivo binário

inicio = time.time()
lzw_compress(data=original_data, file=filename, p=p, static_dictionary=estatico, rc=rc )
fim = time.time()
print("Tempo de Compressão: ", fim - inicio)
print("Dados Comprimidos")

with open(filename, 'rb') as file:
    compressed_data = bitarray()
    compressed_data.fromfile(file)
    #print("Dados do arquivo comprimido: ", compressed_data)

inicio = time.time()
lzw_decompress(data=compressed_data, file="decompressed_"+original_filename, p=p, static_dictionary=estatico, rc=rc)
fim = time.time()
print("Tempo de Descompressão: ", fim - inicio)
#print("Dados descomprimidos: ", decompressed_data)
print("Dados Descomprimidos")

if(os.path.isdir(sys.argv[1])):
    with tarfile.open("decompressed_"+original_filename, "r") as tf:
        tf.extractall()