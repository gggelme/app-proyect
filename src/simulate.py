import random
from datetime import date
from faker import Faker

# Importamos tus modelos y repositorios
from models.persona import Alumno, Profesor
from models.instrumento import Instrumento
from database.alumno_repo import guardar_alumno
from database.profesor_repo import guardar_profesor
from database.instrumento_repo import guardar_instrumento, obtener_todos_instrumentos
from database.alumno_instrumento_repo import asignar_instrumento_a_alumno
from database.pago_repo import obtener_pagos_alumno

fake = Faker('es_AR')

def seccion_bulk_load():
    print("\n🚀 Iniciando carga masiva de Personas...")
    
    # 1. Generar 10 Profesores (IDs 1 al 10 aprox, según tu secuencia)
    for _ in range(10):
        profe = Profesor(
            dni=str(fake.unique.random_int(min=10000000, max=45000000)),
            nombre_apellido=fake.name()[:140],
            fecha_nac=fake.date_of_birth(minimum_age=25, maximum_age=65),
            domicilio=fake.address().replace('\n', ', ')[:190],
            telefono=fake.phone_number(),
            fecha_ingreso=date.today(),
            alias_mp=f"{fake.user_name()}.mp"
        )
        guardar_profesor(profe)
    print("✅ 10 Profesores creados.")

    # 2. Generar 50 Alumnos (IDs 11 al 60 aprox)
    for _ in range(50):
        alu = Alumno(
            dni=str(fake.unique.random_int(min=10000000, max=55000000)),
            nombre_apellido=fake.name()[:140],
            fecha_nac=fake.date_of_birth(minimum_age=6, maximum_age=18),
            domicilio=fake.address().replace('\n', ', ')[:190],
            telefono=fake.phone_number(),
            fecha_ingreso=date.today()
        )
        guardar_alumno(alu)
    print("✅ 50 Alumnos creados.")

def seccion_simulacion_inscripciones():
    print("\n🎸 Simulando inscripciones para alumnos ID 6 al 15...")
    
    instrumentos = obtener_todos_instrumentos()
    if not instrumentos:
        # Si no hay, creamos algunos básicos rápido
        for nombre, precio in [("Piano", 5000), ("Guitarra", 3500), ("Canto", 4000)]:
            guardar_instrumento(Instrumento(nombre=nombre, precio_hora=precio))
        instrumentos = obtener_todos_instrumentos()

    ids_inst = [i.id for i in instrumentos]
    
    # Rango solicitado: del 6 al 15
    for id_alu in range(6, 16):
        # Cada alumno se anota en 1 o 2 cosas
        for _ in range(random.randint(1, 2)):
            id_ins = random.choice(ids_inst)
            horas = random.choice([1, 2])
            desc = random.choice([0.0, 500.0])
            
            # Esto guarda la relación y dispara el PAGO inicial
            asignar_instrumento_a_alumno(id_alu, id_ins, cant_horas=horas, descuento=desc)
    
    print("✅ Inscripciones y pagos automáticos generados.")

def main():
    while True:
        print("\n--- 🎹 SISTEMA ACADEMIA IRUPÉ ---")
        print("1. Carga masiva (Profes y Alumnos)")
        print("2. Simular Inscripciones (Alumnos 6-15)")
        print("3. Ver pagos de un Alumno")
        print("4. Salir")
        
        op = input("Seleccione una opción: ")
        
        if op == "1":
            seccion_bulk_load()
        elif op == "2":
            seccion_simulacion_inscripciones()
        elif op == "3":
            idx = int(input("Ingrese ID del alumno: "))
            pagos = obtener_pagos_alumno(idx)
            for p in pagos: print(f"-> {p}")
        elif op == "4":
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()