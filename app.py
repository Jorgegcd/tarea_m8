import streamlit as st
from check_password import check_password, logout

def main():
    st.title("Tarea Módulo 8: Iniciar Sesión")
    # Leemos el parámetro 'page' de la URL; si no existe, asumimos "login"
    params = st.experimental_get_query_params()
    page = params.get("page", ["login"])[0]

    if page == "login":

        if check_password():
            # Una vez que se loguea, actualizamos el parámetro a "dashboard"
            st.experimental_set_query_params(page="dashboard")
            st.experimental_rerun()
    elif page == "dashboard":
        if st.session_state.get('logged_in', False):        
            st.success("Accediste sin problema")
            st.write("Bienvenido a la aplicación protegida.")
            if st.button("Cerrar Sesión"):
                logout()
        else:
            # Si no está logueado, volvemos al login
            st.experimental_set_query_params(page="login")
            st.experimental_rerun()

if __name__ == "__main__":
    main()