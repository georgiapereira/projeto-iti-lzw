import sys, os

from bitarray import bitarray, frozenbitarray
from bitarray.util import int2ba, ba2int, strip


def initialize_dictionary_encode():
    return {bytes([i]): frozenbitarray(buffer=bytes([i])) for i in range(256)}

def encode(data, dictionary):
    b = 8
    buffer = b'' # ultima frase encontrada no dicionario
    result = bitarray()
    for symbol in data: #
        new_buffer = buffer + bytes([symbol]) 
        if new_buffer in dictionary: 
            buffer = new_buffer 
        else: # quebrou a coincidência 
            tamanho = len(dictionary[buffer])
            if(tamanho < b):
                result = result + bitarray(b - tamanho)
        
            result = result + dictionary[buffer]
            print(result, "int: ", ba2int(dictionary[buffer]), "b:", b, "simbolo: ", buffer)
            dictionary[new_buffer] = frozenbitarray(int2ba(len(dictionary)).to01())
            print("adicionou ao dicionario: ", new_buffer, dictionary[new_buffer])
            newTamanho = len(dictionary[new_buffer])
        
            if(newTamanho > b):
                b = newTamanho
            buffer = bytes([symbol])
            
    if buffer:
        tamanho = len(dictionary[buffer])
        if(tamanho < b):
            result = result + bitarray(b - tamanho)
        result = result + dictionary[buffer]
        print(result, "int: ", ba2int(dictionary[buffer]), "b:", b, "simbolo: ", buffer)
    return result

def lzw_compress(data, static_dictionary=False):
    dictionary = initialize_dictionary_encode()
    #print("Dicionário inicial:", dictionary)
    compressed_data = encode(data, dictionary)
    #print(dictionary)
    return compressed_data

""" def initialize_dictionary_decode():
    return {frozenbitarray(buffer=bytes([i])): bytes([i]) for i in range(256)}

def decode(data, dictionary):
    b = 8
    buffer = b'' # 
    result = b''
    while len(data) > 0: #
        symbol = strip(data[:b], mode="left")
        data = data[b:]
        
        result = result + dictionary[symbol]
        if buffer:
            dictionary[frozenbitarray(int2ba(len(dictionary))).to01()] = buffer + dictionary[symbol]

        if 2 ** b < len(dictionary):
            b = b + 1

        buffer = dictionary[symbol] 
    
    return result

def lzw_decompress(data, static_dictionary=False):
    dictionary = initialize_dictionary_decode()
    decompressed_data = decode(data, dictionary)
    return decompressed_data
 """

file = sys.argv[1]
fin = open(file, "rb")
filename = os.path.splitext(os.path.basename(file))[0]

original_data = fin.read()
fin.close()

compressed_data = lzw_compress(original_data, static_dictionary=True)
print("Dados Comprimidos:", compressed_data)
with open(f"{filename}.bin", 'wb') as output:
    compressed_data.tofile(output)

#compressed_data = bitarray().fromfile(filename+".bin")
#decompressed_data = lzw_decompress(compressed_data)
#print("Dados descomprimidos: ", decompressed_data)


