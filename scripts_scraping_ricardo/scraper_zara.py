from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
import unicodedata
import requests

def scrape_zara_blazers_selenium():
    productos_scrapeados = []
    url_de_las_cateogrias = ["https://www.zara.com/es/es/mujer-faldas-l1299.html?v1=2420454","https://www.zara.com/es/es/mujer-chaquetas-l1114.html?v1=2417772","https://www.zara.com/es/es/mujer-blazers-l1055.html?v1=2420942","https://www.zara.com/es/es/woman-cardigans-sweaters-l8322.html?v1=2419844","https://www.zara.com/es/es/mujer-vestidos-l1066.html?v1=2420896","https://www.zara.com/es/es/mujer-jeans-l1119.html?v1=2419185","https://www.zara.com/es/es/mujer-pantalones-l1335.html?v1=2420796","https://www.zara.com/es/es/mujer-tops-l1322.html?v1=2419940","https://www.zara.com/es/es/mujer-camisas-l1217.html?v1=2420370","https://www.zara.com/es/es/mujer-camisetas-l1362.html?v1=2420417","https://www.zara.com/es/es/mujer-faldas-l1299.html?v1=2420454","https://www.zara.com/es/es/mujer-sudaderas-l1320.html?v1=2467841","https://www.zara.com/es/es/mujer-zapatos-l1251.html?v1=2419160","https://www.zara.com/es/es/mujer-bolsos-l1024.html?v1=2417728","https://www.zara.com/es/es/mujer-prendas-exterior-l1184.html?v1=2419033"]
    
    for categoria in url_de_las_cateogrias:
        try:
            chrome_options = Options()
            #chrome_options.add_argument("--headless")  # Opcional: para no abrir ventana
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=chrome_options)
            driver.get(categoria)
            time.sleep(2)
            boton = driver.find_element(By.ID,"onetrust-reject-all-handler")        
            boton.click()

            original_window = driver.current_window_handle
            botones = driver.find_elements(By.CLASS_NAME,"view-option-selector-button")
            
            botones[1].click()
            
            altura_total = driver.execute_script("return document.body.scrollHeight")
        
            # Posición inicial
            posicion_actual = 0
            
            while posicion_actual < altura_total:
                # Desplazarnos paso a paso
                driver.execute_script(f"window.scrollTo(0, {posicion_actual});")
                time.sleep(0.03)
                
                # Aumentar la posición
                posicion_actual += 100
                
                # Volver a calcular la altura total por si se genera contenido dinámico
                altura_total = driver.execute_script("return document.body.scrollHeight")

            enlaces_de_productos = driver.find_elements(By.CLASS_NAME,"product-link")
            visitados = set()
            for enlace in enlaces_de_productos:
                try:
                    url = enlace.get_attribute("href")
                    if url not in visitados:
                        #print(url)
                        driver.execute_script(f"window.open('{url}','_blank');")
                        time.sleep(1)  # Esperar un poco para que la pestaña abra

                        # 3) Cambiar el foco a la nueva pestaña
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(0.6)
                        enlaces_de_productos3 = driver.find_elements(By.CLASS_NAME,"media__wrapper--media")

                        titulo = driver.find_elements(By.CLASS_NAME,"product-detail-info__header-name")
                        name = titulo[0].get_attribute("innerText")

                        link_foto = ""
                        for urls in enlaces_de_productos3:
                            #print(urls.get_attribute("src"))
                            if urls.get_attribute("src") != None and urls.get_attribute("src").find("-e1.") != -1:
                                link_foto = urls.get_attribute("src")
                                break
                        
                        color_div = driver.find_elements(By.CLASS_NAME, "product-detail-color-selector__color-area")
                        if len(color_div) > 0:
                            for color in color_div:
                                # Ahora localizamos el span dentro de ese div
                                span_element = color.find_element(By.CLASS_NAME,"screen-reader-text")
                                # Extraemos el texto
                                color_name = span_element.get_attribute("innerText")
                                productos_scrapeados.append([url,link_foto,name,color_name.split(" ")[0],categoria.split("-")[1],"zara"])
                        else:
                            color_p = driver.find_elements(By.CLASS_NAME,"product-color-extended-name")
                            color_name = color_p[0].get_attribute("innerText").split(" | ")[0].lower()
                            color_name = color_name.split(" / ")[0]
                            color_name = color_name.split(" - ")[0]
                            color_name = quitar_tildes(color_name)
                            print(color_name)
                            productos_scrapeados.append([url,link_foto,name,color_name.split(" ")[0],categoria.split("-")[1],"zara"])

                        visitados.add(url)
                        #cerrar hemos terminado
                        driver.close()
                        driver.switch_to.window(original_window)
                except:
                    print("Fallo con "+url)
                    driver.close()
                    driver.switch_to.window(original_window)

            driver.quit()
        except:
            print("Error en",categoria)
    return productos_scrapeados

def quitar_tildes(texto):
    texto = texto.lower()  # Convertir a minúsculas
    texto_sin_tildes = ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    )
    return texto_sin_tildes

def crear_csv(data):
    ruta_fichero="data2/ropa_+"+data[0][5]+".csv"
    with open(ruta_fichero, mode='w', newline='', encoding='utf-8') as archivo_original:
        escritor_csv = csv.writer(archivo_original)
        
        # Opción 1: Incluir una fila de cabecera y luego las 4 filas de datos
        escritor_csv.writerow(["reference","image_url","product_name","color","type","shop"])  # Cabecera
        
        for dato in data:
            escritor_csv.writerow(dato)
        


if __name__ == "__main__":

    data = scrape_zara_blazers_selenium()
    crear_csv(data)
    #for item in data:
     #   print(f"Producto: {item[2]}, Imagen: {item[1]}")
