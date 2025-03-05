import streamlit as st
from check_password import check_password, logout

def main():
    st.title("Tarea Módulo 8: Iniciar Sesión")

    if check_password():
        st.write("Bienvenido a la aplicación")
        
        # Aquí va el contenido principal de tu aplicación
        st.write("Contenido protegido de la aplicación")

        # Botón de cierre de sesión
        if st.button("Cerrar Sesión"):
            logout()

if __name__ == "__main__":
    main()