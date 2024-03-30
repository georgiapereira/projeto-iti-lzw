from functools import reduce

def initialize_dictionary():
    #return {bytes([i]): i for i in range(256)}
    return {b'A' : bytes([0]), b'B' : bytes([1]),b'C':bytes([2]),b'D':bytes([3]),b'R': bytes([4])}

def encode(data, dictionary):
    buffer = b'' # ultima frase encontrada no dicionario
    result = []
    for symbol in data: #
        print('Simbolo:', symbol, '\n')
        new_buffer = buffer + bytes([symbol]) 
        if new_buffer in dictionary: 
            buffer = new_buffer 
        else: # quebrou a coincidência 
            result.append(dictionary[buffer]) #
            dictionary[new_buffer] = bytes([len(dictionary)])
            buffer = bytes([symbol]) 
    if buffer:
        result.append(dictionary[buffer])
    return result

def lzw_compress(data, static_dictionary=False):
    dictionary = initialize_dictionary()
    #print("Dicionário inicial:", dictionary)
    compressed_data = encode(data, dictionary)
    return compressed_data


# Exemplo de uso:
original_data = b'ABRACADABRA'
compressed_data = lzw_compress(original_data, static_dictionary=True)
print("Dados Comprimidos:", compressed_data)
