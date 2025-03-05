import streamlit as st
from check_password import check_password, logout

def main():
    st.title("Tarea Módulo 8: Iniciar Sesión")
    # Leemos el parámetro 'page' de la URL; si no existe, asumimos "login"
    params = st.query_params
    page = params.get("page", ["login"])[0]

    if page == "login":

        if check_password():
            # Una vez que se loguea, actualizamos el parámetro a "dashboard"
            st.query_params = {'page':"dashboard"}
            st.rerun()
    elif page == "dashboard":
        if st.session_state.get('logged_in', False):        
            st.success("Accediste sin problema")
            st.write("Bienvenido a la aplicación protegida.")
            if st.button("Cerrar Sesión"):
                logout()
        else:
            # Si no está logueado, volvemos al login
            st.query_params = {"page": "login"}
            st.rerun()
    btnSalir=st.button("Salir")
    if btnSalir:
        st.session_state.clear()
        # Luego de borrar el Session State reiniciamos la app para mostrar la opción de usuario y clave
        st.rerun()
        
if __name__ == "__main__":
    main()