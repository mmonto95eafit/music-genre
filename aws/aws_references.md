# Datalake
### Site with the explanation of datalake zones structure:
https://dzone.com/articles/data-lake-governance-best-practices

Se van a plantear tres zonas:

* **Raw zone:** para la data cruda, en este caso no hay necesidad de encriptar data ya que son canciones.
* **Trusted zone:** Para guardar las features extraidas de las diferentes canciones.
* **Refined Zone:** para guardar la data luego de ser procesada por temas de calidad de datos (outliers, nulls, etc) o las transformaciones para mejorar la efectividad de los modelos aplicados (eliminar campos, normalización, estandarización, etc)
* **Results Zone:** Para guardar la data procesada por modelos o que deba ser consumida por otro componente


## **Raw Zone**:

La raw zone tiene la siguiente estructura de ficheros:
* raw
  * features
    * features_3_sec.csv
  * songs
    * blues
    * classical
    * country
    * disco
    * hiphop
    * jazz
    * metal
    * pop
    * reggae
    * rock



