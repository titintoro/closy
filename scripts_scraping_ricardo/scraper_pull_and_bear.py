from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import csv

def scrape_zara_blazers_selenium():
    productos_scrapeados = []
    url_de_las_cateogrias = ["https://www.pullandbear.com/es/mujer/ropa/cazadoras-y-chaquetas-n6555","https://www.pullandbear.com/es/mujer/ropa/abrigos-n6504","https://www.pullandbear.com/es/mujer/ropa/punto-n6618","https://www.pullandbear.com/es/mujer/ropa/jeans-n6581","https://www.pullandbear.com/es/mujer/ropa/pantalones-n6600","https://www.pullandbear.com/es/mujer/zapatos/ver-todo-n6685","https://www.pullandbear.com/es/mujer/bolsos-n6878","https://www.pullandbear.com/es/mujer/ropa/tops-n6644","https://www.pullandbear.com/es/mujer/ropa/camisetas-n6541","https://www.pullandbear.com/es/mujer/ropa/vestidos-n6646","https://www.pullandbear.com/es/mujer/ropa/sudaderas-n6636","https://www.pullandbear.com/es/mujer/ropa/faldas-n6571","https://www.pullandbear.com/es/mujer/ropa/blusas-y-camisas-n6525","https://www.pullandbear.com/es/mujer/ropa/trajes-n7305"]
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
            '''botones = driver.find_elements(By.CLASS_NAME,"view-option-selector-button")
            
            botones[1].click()'''
            
            altura_total = driver.execute_script("return document.body.scrollHeight")
        
            # Posición inicial
            posicion_actual = 0
            
            while False and posicion_actual < altura_total:
                # Desplazarnos paso a paso
                driver.execute_script(f"window.scrollTo(0, {posicion_actual});")
                time.sleep(0.03)
                
                # Aumentar la posición
                posicion_actual += 100
                
                # Volver a calcular la altura total por si se genera contenido dinámico
                altura_total = driver.execute_script("return document.body.scrollHeight")

            enlaces_de_productos = driver.find_elements(By.CLASS_NAME,"carousel-item-container")
            visitados = set()
            for enlace in enlaces_de_productos:
                
                url = enlace.get_attribute("href")
                if url not in visitados:
                    try:
                        #print(url)
                        driver.execute_script(f"window.open('{url}','_blank');")
                        time.sleep(1.5)  # Esperar un poco para que la pestaña abra

                        # 3) Cambiar el foco a la nueva pestaña
                        driver.switch_to.window(driver.window_handles[-1])
                        time.sleep(0.6)
                        colores = driver.find_elements(By.TAG_NAME, "img")

                        titulo = driver.find_element(By.ID,"titleProductCard")
                        name = titulo.get_attribute("innerText")

                        carrusel_fotos = driver.find_elements(By.TAG_NAME,"product-image-selector")
                        print("Este es")
                        #print(carrusel_fotos[0].get_attribute("dir"))
                        
                        colores_visitados = set()
                        link_foto = ""
                        for urls in colores:
                            #ver colores ya metidos con un set
                            if urls.get_attribute("src").find("-C/") != -1 and urls.get_attribute("src") not in colores_visitados:
                                #print("si va"+ urls.get_attribute("src"))
                                productos_scrapeados.append([url,urls.get_attribute("src").split("?")[0],name,urls.get_attribute("alt").split(" ")[0],categoria.split("/")[6].split("-")[0],"pullandbear"])
                                colores_visitados.add(urls.get_attribute("src"))

                        visitados.add(url)
                        #cerrar hemos terminado
                        driver.close()
                        driver.switch_to.window(original_window)
                    except(Exception) as e:
                        print("Ha fallado el producto: "+url)
                        print(e)
            #driver.execute_script("window.scrollTo(0, 500);")
            #time.sleep(40)



            driver.quit()
        except:
            print("Ha fallado la categoria: "+categoria)
    return productos_scrapeados

def crear_csv(data):
    ruta_fichero="data2/ropa_pullandbear.csv"
    with open(ruta_fichero, mode='w', newline='', encoding='utf-8') as archivo_original:
        escritor_csv = csv.writer(archivo_original)
        
        # Opción 1: Incluir una fila de cabecera y luego las 4 filas de datos
        escritor_csv.writerow(["reference", "image_url", "product_name","color","type","shop"])  # Cabecera
        
        for dato in data:
            escritor_csv.writerow(dato)
        


if __name__ == "__main__":
    data = scrape_zara_blazers_selenium()
    crear_csv(data)
    #for item in data:
        #print(f"Producto: {item[2]}, Imagen: {item[1]}")
        #print(f"Color: {item[3]}")
