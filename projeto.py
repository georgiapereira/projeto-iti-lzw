import sys, os
import math
import time

from bitarray import bitarray, frozenbitarray
from bitarray.util import int2ba, ba2int, strip

def calc_comprimento_medio(n_bit,n_symbol):
    return n_bit/n_symbol

def cal_entropia(dict_cont, n_symbol):
    entropia = 0
    for key_s in dict_cont:
        #print("N: ",n_symbol,"key: ", key_s, "dict_cont[key]:", dict_cont[key_s])
        entropia += (dict_cont[key_s]/n_symbol) * math.log(n_symbol/dict_cont[key_s], 2)
    return entropia
    

def initialize_dictionary_encode():
    return {bytes([i]): frozenbitarray(buffer=bytes([i])) for i in range(256)}

#comprimento médio = numero de bits / simbolos codificados
#entropia = somatorio das informações
#informação = log 1/p
#tempo de compressão e descompressão
def encode(data, dictionary, file, p, static_dictionary):
    n_symbol = 0
    n_bits = 0
    dict_cont_s = {}
    bits_to_write = 64
    b = 8
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
                #print('Bits por simbolo:', dictionary[buffer])
                #print(result, "int: ", ba2int(dictionary[buffer]), "b:", b, "simbolo: ", buffer, "\n")
                tamanho_dict = len(dictionary)
                if (not static_dictionary) or (tamanho_dict < p):
                    dictionary[new_buffer] = frozenbitarray(int2ba(tamanho_dict))
                    
                    newTamanho = len(dictionary[new_buffer])
                    if(newTamanho > b):
                        b = newTamanho

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
            #print('Simbolos: ', result)
            n_bits += len(result)
            write_file.write(result)
            #print(result, "int: ", ba2int(dictionary[buffer]), "b:", b, "simbolo: ", buffer, "\n")
        print ("Comprimento médio:", calc_comprimento_medio(n_bits,n_symbol))
        print ("Entropia: ", cal_entropia(dict_cont_s,n_symbol))
def lzw_compress(data, file, p, static_dictionary=False):
    dictionary = initialize_dictionary_encode()
    #print("Dicionário inicial:", dictionary)
    encode(data, dictionary, file, p, static_dictionary)
    #print(dictionary)

def initialize_dictionary_decode():
    return {frozenbitarray(buffer=bytes([i])): bytes([i]) for i in range(256)}

def decode(data, dictionary, file, p, static_dictionary):
    data_len = len(data)
    b = 8
    buffer = b'' # 
    result = b''
    cur_index = 0
    with open(file, 'wb') as write_file:
        while True: #
            symbol = strip(data[cur_index:b+cur_index], mode="left") #2
            #symbol = data[:b] #2
            #if(len(symbol) == 0): symbol = bitarray('0')
            #print(data[:b], symbol, b)
            #data = data[b:] #eof
            cur_index = cur_index + b

            if len(symbol) < 8:
                symbol = bitarray(8 - len(symbol)) + symbol

            frozen_symbol = frozenbitarray(symbol)

            dict_len = len(dictionary)
            if (not static_dictionary) or (dict_len < p):
                if buffer:
                    if frozen_symbol not in dictionary:
                        dictionary[frozenbitarray(int2ba(dict_len))] = buffer + bytes([buffer[0]]) 
                    else:
                        dictionary[frozenbitarray(int2ba(dict_len))] = buffer + bytes([dictionary[frozen_symbol][0]]) 

                if 2 ** b <= len(dictionary) and 2 ** b < p:
                    b = b + 1 #6
            
            #print(result, "int: ", ba2int(symbol), "b:", b, "simbolo: ", dictionary[frozenbitarray(symbol)], "\n")
           
            result = result + dictionary[frozen_symbol] #a,a,b,ab,aba, aa

            buffer = dictionary[frozen_symbol]  #aa

            if(len(result) >= 2 ** 12):
                write_file.write(result)
                result = b''

            if cur_index >= data_len:
                break

        if result:
            write_file.write(result)

    
def lzw_decompress(data, file, p, static_dictionary=False):
    dictionary = initialize_dictionary_decode()
    decode(data, dictionary, file, p, static_dictionary)

p = 2 ** 12

file = sys.argv[1]
fin = open(file, "rb")
filename = os.path.splitext(os.path.basename(file))[0]
original_filename = filename + os.path.splitext(os.path.basename(file))[1]

original_data = fin.read()
#print(original_data, "\n")
fin.close()

filename = f"compressed_{filename}.bin"  # Substitua "seu_arquivo.bin" pelo nome do seu arquivo binário

inicio = time.time()
lzw_compress(data=original_data, file=filename, p=p, static_dictionary=True, )
fim = time.time()
print("Tempo de Compressão: ", fim - inicio)
print("Dados Comprimidos")
with open(filename, 'rb') as output:
    pass
    #print(output.read())
    #compressed_data.tofile(output)

with open(filename, 'rb') as file:
    compressed_data = bitarray()
    compressed_data.fromfile(file)
    #print("Dados do arquivo comprimido: ", compressed_data)

inicio = time.time()
lzw_decompress(data=compressed_data, file="decompressed_"+original_filename, p=p, static_dictionary=True)
fim = time.time()
print("Tempo de Descompressão: ", fim - inicio)
#print("Dados descomprimidos: ", decompressed_data)
print("Dados Descomprimidos")

with open("decompressed_"+original_filename, 'rb') as file:
    pass
    #file.write(decompressed_data)



