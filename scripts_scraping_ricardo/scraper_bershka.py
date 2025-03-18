from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv
import requests

def scrape_zara_blazers_selenium():
    productos_scrapeados = []
    url_de_las_cateogrias = ["https://www.bershka.com/us/es/mujer/ropa/cazadoras-n4364.html"]
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
    
        
        altura_total = driver.execute_script("return document.body.scrollHeight")
    
        # Posición inicial
        posicion_actual = 0
        
        while posicion_actual < 2000:
            # Desplazarnos paso a paso
            driver.execute_script(f"window.scrollTo(0, {posicion_actual});")
            time.sleep(0.05)
            
            # Aumentar la posición
            posicion_actual += 100
            
            # Volver a calcular la altura total por si se genera contenido dinámico
            altura_total = driver.execute_script("return document.body.scrollHeight")
        time.sleep(2)

        enlaces_de_productos = driver.find_elements(By.CSS_SELECTOR,"div.category-product-card")
        visitados = set()
        for enlace in enlaces_de_productos:
            aux = enlace.find_element(By.CSS_SELECTOR,"a.grid-card-link")
            url = aux.get_attribute("href")
            if url not in visitados:
                
                #print(url)
                driver.execute_script(f"window.open('{url}','_blank');")
                time.sleep(1)  # Esperar un poco para que la pestaña abra

                # 3) Cambiar el foco a la nueva pestaña
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(0.6)
                enlaces_de_productos3 = driver.find_elements(By.CLASS_NAME, "image-item")
                titulo = driver.find_elements(By.CSS_SELECTOR,"h1.product-detail-info-layout__title")
                name = titulo[0].get_attribute("innerText")

                time.sleep(1)

                link_foto = ""
                for urls in enlaces_de_productos3:
                    #print(urls.get_attribute("src"))
                    if urls.get_attribute("src") != None and urls.get_attribute("src").find("-a4o") != -1:
                        link_foto = urls.get_attribute("src")
                        break
                
                color_div = driver.find_elements(By.CSS_SELECTOR, "li.round-color-picker__color")
                if len(color_div) > 0:
                    for color in color_div:
                        # Ahora localizamos el span dentro de ese div
                        img = color.find_element(By.CSS_SELECTOR,"img.image-item")
                        # Extraemos el texto
                        color_name = img.get_attribute("alt")
                        productos_scrapeados.append([url,link_foto,name,color_name.split(" ")[0],categoria.split("/")[5].split("-")[0],"bershka"])
                        print([url,link_foto,name,color_name.split(" ")[0],categoria.split("/")[5].split("-")[0],"bershka"])
                else:
                    color_p = driver.find_elements(By.CSS_SELECTOR,"div.product-reference")
                    color_name = color_p[0].get_attribute("innerText").split(" · ")[0]
                    productos_scrapeados.append([url,link_foto,name,color_name.split(" ")[0],categoria.split("/")[5].split("-")[0],"bershka"])
                    print([url,link_foto,name,color_name.split(" ")[0],categoria.split("/")[5].split("-")[0],"bershka"])

                visitados.add(url)
                #cerrar hemos terminado
                driver.close()
                driver.switch_to.window(original_window)
                try:
                    print("")
                except:
                    print("liada")
                    driver.close()
                    driver.switch_to.window(original_window)
        
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
