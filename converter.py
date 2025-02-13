import re
import yaml
import os
from pathlib import Path

DECIMAL_PLACES = 3

LAYER_KEY_ORDER = [
    ["description"],
    ["rho", "resistivity", "conductivity"],
    ["t", "thickness"],
    ["eps", "permittivity"]
]
METAL_KEY_ORDER = [
    ["description"],
    ["layer"],
    ["rsh", "sheet_resistance", "resistivity", "conductivity"],
    ["t", "thickness"],
    ["d", "distance"],
    ["name"],
    ["color"],
    ["gds-number"],
    ["gds-datatype"]
]
VIA_KEY_ORDER = [
    ["description"],
    ["top", "top_metal"],
    ["bottom", "bottom_metal"],
    ["r", "resistance", "resistivity", "conductivity"],
    ["thickness"],
    ["width", "min_width"],
    ["space"],
    ["overplot1", "enclosure"],
    ["overplot2", "endcap_enclosure"],
    ["name"],
    ["color"],
    ["gds-number"],
    ["gds-datatype"],
]

def convert_keys(input_dict: dict[str, any], conversions_list: list[list[str]], output_type: str) -> dict[str, any]:
    """
    Converte as chaves de um dicionário com base em uma lista de listas de conversão e tipo de saída.
    :param input_dict: Dicionário de entrada.
    :param conversions_list: Lista de listas de conversão com nomes equivalentes.
    :param output_type: Tipo de saída desejado ("tech" ou "tek").
    :return: Dicionário com chaves convertidas.
    """
    converted_dict = {}

    for key, value in input_dict.items():
        # Procura a chave no conjunto correto
        for conversion_list in conversions_list:
            if key in conversion_list:
                if output_type == "tech":
                    # O segundo elemento da lista é o nome de saída para "tech"
                    converted_name = conversion_list[1]
                else:
                    # O primeiro elemento da lista é o nome de saída para "tek"
                    converted_name = conversion_list[0]
                converted_dict[converted_name] = value
                break
        else:
            # Se não houver conversão, mantém a chave original
            converted_dict[key] = value

    return converted_dict


def convert_techfile_keys(techfile: dict[str, list[dict[str, any]]], output_type: str) -> dict[str, list[dict[str, any]]]:
    """
    Converte os nomes das chaves dos elementos do techfile.
    :param techfile: Dicionário contendo listas de elementos com chaves a serem convertidas.
    :param output_type: Tipo de saída desejado ("tech" ou "tek").
    :return: Techfile com chaves convertidas.
    """
    techfile_aux = {}

    # Lista de conversões de nomes
    conversions_list: list[list[str]] = [
        ["rho", "resistivity"],
        ["eps", "permittivity"],
        ["t", "thickness"],
        ["r", "resistance"],
        ["rsh", "sheet_resistance"],
        ["d", "distance"],
        ["top", "top_metal"],
        ["bottom", "bottom_metal"],
        ["overplot1", "enclosure"],
        ["overplot2", "endcap_enclosure"],
        ["width", "min_width"]
    ]

    # Converte as chaves de cada elemento nas listas do techfile
    for layer_type, elements in techfile.items():
        converted_elements = [
            convert_keys(element, conversions_list, output_type) for element in elements
        ]
        techfile_aux[layer_type] = converted_elements

    return techfile_aux

def convert_techfile_to_default(techfile: dict[str, list[dict[str, any]]]) -> dict[str, list[dict[str, any]]]:
    """
    Converte elementos de um techfile para valores padrão, realizando cálculos específicos
    baseados no tipo de camada (layer, metal ou via).
    :param techfile: Dicionário com listas de elementos do techfile.
    :return: Techfile com valores convertidos para o formato padrão.
    """

    def to_default(element: dict[str, any], layer_type: str) -> dict[str, any]:
        """
        Converte um único elemento para valores padrão, baseando-se no tipo de camada.
        :param element: Dicionário representando um elemento da camada.
        :param layer_type: Tipo de camada (layer, metal ou via).
        :return: Dicionário do elemento convertido.
        """
        converted_element = {}

        # Operações específicas para camadas de tipo "layer"
        if layer_type == "layer":
            if "conductivity" in element:
                for key, value in element.items():
                    if key == "conductivity":
                        converted_element["resistivity"] = round((1 / value) * 100, DECIMAL_PLACES)
                    else:
                        if key in ["thickness", "permittivity"]:
                            converted_element[key] = round(value, DECIMAL_PLACES)
                        else:
                            converted_element[key] = value

        # Operações específicas para camadas de tipo "metal"
        elif layer_type == "metal":
            thickness_meters = element.get("thickness", 0) * 1e-6  # Converter para metros
            if "conductivity" in element:
                for key, value in element.items():
                    if key == "conductivity":
                        resistivity = (1 / value)
                        converted_element["sheet_resistance"] = round((resistivity / thickness_meters) * 1000, DECIMAL_PLACES)
                    else:
                        if key in ["thickness", "distance"]:
                            converted_element[key] = round(value, DECIMAL_PLACES)
                        else:
                            converted_element[key] = value
            elif "resistivity" in element:
                for key, value in element.items():
                    if key == "resistivity":
                        resistivity = (value / 100)
                        converted_element["sheet_resistance"] = round((resistivity / thickness_meters) * 1000, DECIMAL_PLACES)
                    else:
                        if key in ["thickness", "distance"]:
                            converted_element[key] = round(value, DECIMAL_PLACES)
                        else:
                            converted_element[key] = value
            else:
                for key, value in element.items():
                    if key in ["sheet_resistance", "thickness", "distance"]:
                        converted_element[key] = round(value, DECIMAL_PLACES)
                    else:
                        converted_element[key] = value

        # Operações específicas para camadas de tipo "via"
        elif layer_type == "via":
            thickness_meters = element.get("thickness", 0) * 1e-6  # Converter para metros
            width_meters = element.get("min_width", 0) * 1e-6  # Converter para metros
            if "conductivity" in element:
                for key, value in element.items():
                    if key == "conductivity":
                        resistivity = (1 / value)
                        area = width_meters**2
                        converted_element["resistance"] = round((resistivity * thickness_meters) / area, DECIMAL_PLACES)
                    elif key != "thickness":
                        if key in ["min_width", "space", "enclosure", "endcap_enclosure"]:
                            converted_element[key] = round(value, DECIMAL_PLACES)
                        else:
                            converted_element[key] = value
            elif "resistivity" in element:
                for key, value in element.items():
                    if key == "resistivity":
                        resistivity = (value / 100)
                        area = width_meters**2
                        converted_element["resistance"] = round((resistivity * thickness_meters) / area, DECIMAL_PLACES)
                    elif key != "thickness":
                        if key in ["min_width", "space", "enclosure", "endcap_enclosure"]:
                            converted_element[key] = round(value, DECIMAL_PLACES)
                        else:
                            converted_element[key] = value
            else:
                for key, value in element.items():
                    if key in ["resistance", "min_width", "space", "enclosure", "endcap_enclosure"]:
                        converted_element[key] = round(value, DECIMAL_PLACES)
                    else:
                        converted_element[key] = value

        # Retorna o elemento convertido ou original se nenhuma conversão foi aplicada
        return converted_element or element

    # Processa cada tipo de camada no techfile
    converted_techfile = {}
    for layer_type, elements in techfile.items():
        converted_techfile[layer_type] = [to_default(element, layer_type) for element in elements]

    return converted_techfile


def convert_techfile_values(techfile: dict[str, list[dict[str, any]]]) -> dict[str, list[dict[str, any]]]:
    """
    Converte apenas os valores dos elementos em um techfile.
    """
    def value_conversion(value):
        if value is None:
            return value
        try:
            int_value = int(value)
            return int_value
        except ValueError:
            try:
                float_value = round(float(value), DECIMAL_PLACES)
                return float_value
            except ValueError:
                return value

    converted_techfile = {}

    for layer_type, elements in techfile.items():
        converted_elements = []
        for element in elements:
            converted_element = {key: value_conversion(value) for key, value in element.items()}
            converted_elements.append(converted_element)
        converted_techfile[layer_type] = converted_elements

    return converted_techfile


def reorder_dict(input_dict:dict[str], key_order:list[str]):
    """
    Reorganiza um dicionário seguindo múltiplas alternativas de organização.
    :param input_dict: Dicionário a ser reorganizado.
    :param key_order_alternatives: Lista de listas com as alternativas de organização.
    :return: Dicionário reorganizado.
    """
    ordered_dict = {}

    # Itera pelas alternativas de ordem
    for group in key_order:
        for key in group:
            # Adiciona a chave ao dicionário reorganizado se ela existir no dicionário original
            if key in input_dict:
                ordered_dict[key] = input_dict[key]
                break  # Para no primeiro elemento encontrado no grupo

    # Adiciona quaisquer chaves restantes que não foram incluídas
    extras = {key: input_dict[key] for key in input_dict if key not in ordered_dict}
    ordered_dict.update(extras)

    return ordered_dict

def reorder_techfile(techfile:dict[str, list[dict[str, any]]]) -> dict[str, list[dict[str, any]]]:

    techfile_aux = dict()

    for layer_type in techfile:
        aux = []
        key_order = LAYER_KEY_ORDER if layer_type == "layer" else METAL_KEY_ORDER if layer_type == "metal" else VIA_KEY_ORDER
        for layer_element_index in range(len(techfile[layer_type])):
            aux.append(reorder_dict(techfile[layer_type][layer_element_index], key_order=key_order))
        techfile_aux[layer_type] = aux
    
    return techfile_aux

def chip_params(file_path:str):
    return f"""<chip>
    chipx = 512
    chipy = 512
    fftx = 128
    ffty = 128
    TechFile = {os.path.basename(file_path)}
    TechPath = .
    eddy = 0
"""

def process_user_path(user_input: str, correct_extension: str) -> str:
    """
    Processa o caminho fornecido pelo usuário.
    - Verifica se o caminho é absoluto ou relativo e resolve-o.
    - Garante que o arquivo possui a extensão correta, adicionando ou substituindo, se necessário.
    
    :param user_input: Caminho do arquivo fornecido pelo usuário.
    :param correct_extension: Extensão correta para o arquivo (com ou sem o ponto).
    :return: Caminho completo com a extensão correta.
    """
    # Garantir que a extensão fornecida comece com um ponto
    if not correct_extension.startswith("."):
        correct_extension = f".{correct_extension}"

    # Resolver o caminho, tratando absoluto ou relativo
    file_path = Path(user_input).resolve()

    # Verificar se o arquivo tem uma extensão
    if file_path.suffix:
        # Comparar a extensão existente com a correta
        if file_path.suffix != correct_extension:
            file_path = file_path.with_suffix(correct_extension)
    else:
        # Adicionar a extensão correta se não houver extensão
        file_path = file_path.with_suffix(correct_extension)

    return str(file_path)

def write_tech(techfile:dict[str, list[dict[str, any]]], file_path:str):

    with open(process_user_path(file_path, ".tech"), "w") as file:
        yaml.dump(techfile, file, allow_unicode=True, sort_keys=False)

def write_tek(techfile:dict[str, list[dict[str, any]]], file_path:str):

    file_path = process_user_path(file_path, ".tek")

    techfile = convert_techfile_to_default(techfile=techfile)
    techfile = convert_techfile_keys(techfile=techfile, output_type="tek")
    
    with open(file_path, "w") as file:
        file.write(f"{chip_params(os.path.basename(file_path))}\n")
        for layer_type in techfile:
            if layer_type != "chip":
                for params_index in range(len(techfile[layer_type])):
                    params = techfile[layer_type][params_index]
                    file.write(f"<{layer_type}> {params_index} ; {params['description']}\n")
                    params.pop("description", None)
                    for param_name in params:
                        if not param_name in ("gds_number", "gds_datatype"):
                            param_value = params[param_name]
                            file.write(f"    {param_name} = {param_value}\n")
                    file.write("\n")


def load_tech(file_path:str) -> dict[str, list[dict[str, any]]]:

    file_path = process_user_path(file_path, ".tech")

    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def load_tek(file_path:str):

    file_path = process_user_path(file_path, ".tek")

    current_header = None
    current_index = None
    loaded_techfile: dict[str, list] = dict()

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()

            # Ajustado para permitir ausência de índice e descrição
            header = re.match(r"<([^>\s]+)>\s*(\d+)?\s*(?:;\s*(.*))?", line)
            key_value = re.match(r"(.*?)=(.*?)(?:\s*;.*)?$", line)

            if header:
                current_header = header.group(1)  # HEADER
                current_index = int(header.group(2)) if header.group(2) else len(loaded_techfile.get(current_header, []))  # INDEX ou próximo índice

                if current_header not in loaded_techfile:
                    loaded_techfile[current_header] = []
                # Adiciona descrição, mesmo se for None
                loaded_techfile[current_header].insert(current_index, {"description": header.group(3)}) 

            elif key_value:
                key = key_value.group(1).strip()
                value = key_value.group(2).strip()
                if current_header is not None:  # Só adiciona se houver um cabeçalho ativo
                    loaded_techfile[current_header][current_index][key] = value

    loaded_techfile.pop("chip", None)

    loaded_techfile = reorder_techfile(techfile=loaded_techfile)
    loaded_techfile = convert_techfile_keys(techfile=loaded_techfile, output_type="tech")
    loaded_techfile = convert_techfile_values(techfile=loaded_techfile)

    # Exibe o resultado formatado como JSON
    return loaded_techfile