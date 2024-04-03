from bitarray import bitarray, frozenbitarray
from bitarray.util import int2ba, ba2int


def initialize_dictionary():
    #return {bytes([i]): i for i in range(256)}
    return {
        b'A' : frozenbitarray('000'), 
        b'B' : frozenbitarray('001'),
        b'C' : frozenbitarray('010'),
        b'D' : frozenbitarray('011'),
        b'R' : frozenbitarray('100')
    }

def encode(data, dictionary):
    b = 3
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
    dictionary = initialize_dictionary()
    #print("Dicionário inicial:", dictionary)
    compressed_data = encode(data, dictionary)
    print(dictionary)
    return compressed_data


# Exemplo de uso:
original_data = b'ABRACADABRA'
compressed_data = lzw_compress(original_data, static_dictionary=True)
print("Dados Comprimidos:", compressed_data)
with open("output.bin", 'wb') as output:
    compressed_data.tofile(output)
