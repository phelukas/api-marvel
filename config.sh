#!/bin/bash

# Verifica se foram fornecidos argumentos suficientes
if [ $# -ne 2 ]; then
  # echo "Uso: $0 <nome_do_contêiner> <nome_da_variável>"
  exit 1
fi

# Nome do contêiner passado como argumento
container_name="$1"

# Nome da variável passado como argumento
variable_name="$2"

# Executa o comando "docker start" para ligar o contêiner
docker start $container_name
container_info=$(docker inspect "$container_name" 2>/dev/null)

# Executa o comando "docker inspect" para obter as informações do contêiner
container_info=$(docker inspect "$container_name" 2>/dev/null)

# Verifica se o contêiner existe
if [ $? -ne 0 ]; then
  echo "O contêiner não existe."
  exit 1
fi

# Extrai o endereço IP do contêiner usando expressões regulares
ip_address=$(echo "$container_info" | grep -m 1 -Eo '"IPAddress": "[^"]+"' | awk -F'"' '{print $4}')

# echo \"$ip_address\"

# Atualiza a variável passada no arquivo .env com o endereço IP
sed -i "s/$variable_name = "".*/$variable_name = \"$ip_address\"/" .env

# Verifica se a atualização da variável no arquivo .env foi bem-sucedida
if [ $? -ne 0 ]; then
  echo "Erro ao atualizar a variável $variable_name no arquivo .env."
  exit 1
fi

# echo "Endereço IP do contêiner '$container_name': \"$ip_address\""

# Verifica se a variável já está definida no arquivo .env
if grep -q "$variable_name =" .env; then
  # Atualiza a variável no arquivo .env com o endereço IP
  sed -i "s/$variable_name =.*/$variable_name = \"$ip_address\"/" .env
  # echo "Variável $variable_name atualizada no arquivo .env com o endereço IP."
else
  # Adiciona a variável ao arquivo .env com o endereço IP em uma nova linha
  echo -e "\n$variable_name = \"$ip_address\"" >> .env
  # echo "Variável $variable_name adicionada ao arquivo .env com o endereço IP."
fi
