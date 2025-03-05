import streamlit as st
from check_password import check_password, logout

def main():
    # Leemos el parámetro 'page' de la URL; si no existe, asumimos "login"
    params = st.query_params
    page = params.get("page", ["login"])[0]

    if page == "login":
        st.title("Tarea Módulo 8: Iniciar Sesión")
        if check_password():
            # Una vez que se loguea, actualizamos el parámetro a "dashboard"
            st.set_query_params(page="dashboard")
            st.rerun()

    elif page == "dashboard":
        if st.session_state.get('logged_in', False):        
            st.success("Accediste sin problema")
            st.write("Bienvenido a la aplicación protegida.")
            btnSalir = st.button("Cerrar Sesión")
            if btnSalir:
                logout()
        else:
            # Si no está logueado, volvemos al login
            st.set_query_params(page="login")
            st.rerun()

if __name__ == "__main__":
    main()
