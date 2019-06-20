from PIL import Image
import face_recognition
from django.http import HttpResponse, JsonResponse
import numpy
import PIL
import cv2
import re
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt)
def recognize_image(request, format=None):
    selfie_array = face_recognition.load_image_file(request.FILES[
                                                        'img_selfie'])  # 1 Passa por paramêtro uma conversão direta de InMemoryUploadedFile para b'', que retorna um narray
    document_array = face_recognition.load_image_file(request.FILES['img_document'])
    face_location_selfie, face_location_document, erro = detect_faces(selfie_array, document_array)
    if (len(erro) > 0):
        return HttpResponse(str(erro))

    # 2 Coleta a posição do rosto nas duas imagens
    face_selfie = face_position(face_location_selfie)
    face_document = face_position(face_location_document)
    # 3 Corta da imagem original o rosto detectado nos dois documentos
    cropped_selfie = crop_image(selfie_array, face_selfie)
    cropped_document = crop_image(document_array, face_document)
    # 4 Diminui ou Aumenta o tamanho da Selfie baseado no tamanho do Documento
    size_document = Image.fromarray(cropped_document).size
    resized_selfie = resize_selfie(cropped_selfie, size_document)
    similar, result = compare_two_pictures(cropped_document, resized_selfie)
    # 5 pega altura e largura da imagem
    width, height = get_num_pixels(cropped_document)
    area_doc = height * width

    if (result == []):
        return HttpResponse('O Robô não conseguiu determinar se há semelhança nas imagens. Favor re-enviar outras')
    if (result[0] == True):
        response = {"Resultado": str(result[0]),
                    "Similaridade": str(round((1 - similar[0]) * 100, 2)),
                    "Message": "Documento Validado com Sucesso"}
        return JsonResponse(response)
    else:
        return HttpResponse('Documento Não Validado')


def detect_faces(selfie_array, document_array):  # ENCONTRA FACES NA IMAGEM, APLICA FILTRO E RETORNA POSIÇÃO DOS ROSTOS
    face_location_selfie = face_recognition.face_locations(selfie_array)
    face_location_document = face_recognition.face_locations(document_array)
    erro = []
    if (len(face_location_selfie) < 1 or len(face_location_document) < 1):  # Se não há face em um dos dois
        return None, None, (
            "Não foi encontrado rosto em uma das (ou em ambas) fotos. Rostos encontrados: Selfie: {} Documento: {}".format(
                len(face_location_selfie), len(face_location_document)))
    if (len(face_location_selfie) > 1):
        return None, None, ("Mais de um rosto na selfie. Favor mandar uma com você somente.")
    if (len(face_location_document) > 1):
        for index in range(0, len(
                face_location_document)):  # Verificar Rostos encontrados no documento. Se mais de um válido: Cancele. Se um só passar, transforme face_locations para ele.
            converter = numpy.asarray(face_location_document[index])
            new_list = []
            new_list.append(converter)
            try:
                possible_face_area = []
                possible_face_area = face_position(new_list)
                possible_face = crop_image(document_array, possible_face_area)
                lixo, result = compare_two_pictures(possible_face, selfie_array)
                if (result != []):
                    if (result[0] == True):
                        face_location_document = new_list[index]
            except IndexError:
                return None, None, ("Não fora detectado nenhum rosto neste documento")
    try:
        document_encoding = face_recognition.face_encodings(document_array)[0]
        selfie_encoding = face_recognition.face_encodings(selfie_array)[0]
    except IndexError:
        return None, None, "Não foi possível encontrar nenhum rosto em nenhuma das imagens. Avalie os arquivos das imagens enviadas."
        quit()
    # print("Encontrado {} rosto nesta selfie.".format(len(face_location_selfie)))
    return face_location_selfie, face_location_document, []


def face_position(face_location):  # RETORNA A LOCALIZAÇÃO (TOP, BOTTOM, LEFT, RIGHT) DA IMAGEM PASSADA
    for face in face_location:
        # Print the location of each face in this image
        top, right, bottom, left = face
    area = top, bottom, left, right
    return area


def crop_image(image_array, face_location):
    # Acessar a posição do rosto e recortar ele da imagem, passada como numpy array
    face_selfie = image_array[face_location[0]:face_location[1],
                  face_location[2]:face_location[3]]  # Top:Bottom, Left:Right
    # pil_selfie = Image.fromarray(face_selfie) #Conversão para Image Object
    # pil_selfie.save("crop_result.jpg") #Salvando no diretorio a imagem cortada
    return face_selfie


def resize_selfie(selfie, size: ()):
    selfie_resized = cv2.resize(selfie, dsize=size, interpolation=cv2.INTER_NEAREST)
    # Image.Image.save(Image.fromarray(selfie_resized), 'selfie_cropped_resized.jpg')
    return selfie_resized


# FILTER
def compare_two_pictures(document, selfie):
    encoded_document = face_recognition.face_encodings(document)  # Transforma o rosto encontrado em código
    encoded_selfie = face_recognition.face_encodings(selfie)
    similar = face_recognition.face_distance(encoded_document,
                                             encoded_selfie[0])  # Compara o quão similar os rostos são
    result = face_recognition.compare_faces(encoded_document, encoded_selfie[0],
                                            tolerance=0.55)  # Compara os rostos para dizer se são da mesma pessoa
    #   #quanto menor a tolerância, mais rígida a comparação
    return similar, result


def get_num_pixels(image):  # Recebe um numpy array
    width, height = PIL.Image.fromarray(numpy.uint8(image)).size
    return width, height


def saveOnBucket():
    return "Succeful"


# FILTER
def quality(cropped_selfie):
    get_num_pixels(cropped_selfie)
    return "Tipo de documento não encontrado"


##FILTER
def same_pic(selfie, document):  # Aqui recebe dois arrays
    if (numpy.equal(selfie, document)):
        return False
    return True


##AUTH
def validate_request():
    return 1


# TESSERACT
# def catch_ocr(image):
#     text = ocr.image_to_string(image, lang="por")
#     # if(image != [] or image != None):
#     # ocrmypdf.leptonica.deskew("teste2.png", "teste2.png", 300) #Atribuir DPI e "endireitar" imagem
#     # ocrmypdf.leptonica.remove_background("teste2.png", "teste2235.png")
#     return text

##REGEX
def regex_cpf(imageOcr):
    pre_result = re.search("((\d{3}[\D\s]{0,2})){3}\d{2}", imageOcr)
    if (pre_result != None):
        result = pre_result.group()
        cpf = re.findall("(\\d)", result)
        cpf = [''.join(cpf[0: len(cpf)])]
        return cpf[0]
    else:
        return "Não foi encontrado nenhum CPF"


##REGEX
def regex_cnh_dates(imageOcr):
    result = re.findall("\d\d\D\d\d\D\d\d\d\d", imageOcr)
    nascimento, validade, primeira_hab, data_de_emissao = result
    return nascimento, validade, primeira_hab, data_de_emissao


##OPENCV
def detect_border(area_doc):
    img = cv2.imread('teste.jpg', cv2.IMREAD_GRAYSCALE)
    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    # thresh = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C, thresholdType=cv2.THRESH_BINARY_INV, blockSize=101, C=2)
    thresh_type = "ADBINARY_INV"
    contador = 0

    PIL.Image.fromarray(numpy.uint8(thresh)).save("thresh" + str(thresh_type) + ".png")

    contours, hierarchy = cv2.findContours(thresh, 1, 2)
    for cnt in contours:
        ##STRAIGHT BOUNDING RETANGLE
        ##SEM IF
        # x, y, w, h = cv2.boundingRect(cnt)
        # img2 = cv2.imread('doc_pic.jpg', cv2.IMREAD_COLOR)
        # cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # PIL.Image.fromarray(numpy.uint8(img2)).save("./teste/docNumber"+str(contador)+".png")
        # contador =contador + 1
        ##COM IF
        area = cv2.contourArea(cnt)
        if (area > area_doc and area != area_doc):
            x, y, w, h = cv2.boundingRect(cnt)
            b = y, y + h, x, x + w
            img2 = cv2.imread('teste.jpg', cv2.IMREAD_COLOR)
            a = crop_image(img2, b)
            try:
                c, result1 = compare_two_pictures(a, img2)
                if (result1[0] == True):
                    cv2.rectangle(img2, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    PIL.Image.fromarray(numpy.uint8(a)).save("docNumber.png")
                    # PIL.Image.fromarray(numpy.uint8(a)).save("./teste/doc"+str(thresh_type)+"Number" + str(contador) + "R,C:"+str(RETR)+str(CHAIN)+".png")
            except IndexError:
                0
            contador = contador + 1
    return 1
