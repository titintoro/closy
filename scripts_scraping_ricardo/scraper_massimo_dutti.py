from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
import requests

def scrape_zara_blazers_selenium():
    productos_scrapeados = []
    url_de_las_cateogrias = ["https://www.massimodutti.com/es/s/w-jackets-n3375"]
    
    for categoria in url_de_las_cateogrias:
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
        
        #altura_total = driver.execute_script("return document.body.scrollHeight")
        altura_total=2000
        print(altura_total)
        time.sleep(1)
    
        # Posición inicial
        posicion_actual = 0
        
        altura_scroll = 200  # píxeles a desplazar en cada paso
        for _ in range(100):   # número de repeticiones
            driver.execute_script(f"arguments[0].scrollTop += {altura_scroll}", driver.find_element(By.TAG_NAME,"html"))
            time.sleep(0.03)
        time.sleep(1.5)
        print("finished")
        enlaces_de_productos = driver.find_elements(By.CSS_SELECTOR,"li.grid-product")
        
        visitados = set()
        for enlace in enlaces_de_productos:
            enlace2 = enlace.find_elements(By.TAG_NAME,"a")
            url = enlace2[0].get_attribute("href")
            if url not in visitados:
                try:
                    #print(url)
                    driver.execute_script(f"window.open('{url}','_blank');")
                    time.sleep(1)  # Esperar un poco para que la pestaña abra

                    # 3) Cambiar el foco a la nueva pestaña
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(2)
                    scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.cc-imagen-collection")

                    # Opción 1: Desplazamiento completo hasta el final
                    altura_scroll = 200  # píxeles a desplazar en cada paso
                    for _ in range(20):   # número de repeticiones
                        driver.execute_script(f"arguments[0].scrollTop += {altura_scroll}", scrollable_div)
                        time.sleep(0.03)

                    time.sleep(1)
                    enlaces_de_productos3 = driver.find_elements(By.CLASS_NAME,"product-media__img")

                    titulo = driver.find_elements(By.CSS_SELECTOR,"h1.product-name")
                    name = titulo[0].get_attribute("innerText")

                    link_foto = ""
                    for urls in enlaces_de_productos3:
                        #print(urls.get_attribute("src"))
                        url_foto = urls.find_elements(By.TAG_NAME,"img")
                        if len(url_foto)>0 and url_foto[0].get_attribute("src") != None and url_foto[0].get_attribute("src").find("-o1") != -1 and url_foto[0].get_attribute("src").find("-o11") == -1:
                            link_foto = url_foto[0].get_attribute("src")
                            break
                    
                    colores_usados=set()
                    color_div = driver.find_elements(By.ID, "product-color-selector")
                    if len(color_div) > 0:
                        for color in color_div:
                            # Ahora localizamos el span dentro de ese div
                            img = color.find_element(By.TAG_NAME,"img")
                            # Extraemos el texto
                            color_name = img.get_attribute("alt")
                            if color_name not in colores_usados:
                                colores_usados.add(color_name)
                                productos_scrapeados.append([url,link_foto.split("?")[0],name,color_name.split(" ")[0],categoria.split("/")[5].split("-")[1],"massimodutti"])
                    

                    visitados.add(url)
                    #cerrar hemos terminado
                    driver.close()
                    driver.switch_to.window(original_window)
                except:
                    driver.close()
                    driver.switch_to.window(original_window)
                    print("nada tio no hubo suerte")
        #driver.execute_script("window.scrollTo(0, 500);")
        #time.sleep(40)

        driver.quit()
    return productos_scrapeados

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
    for item in data:
        print(f"Producto: {item[2]}, Imagen: {item[1]}")
