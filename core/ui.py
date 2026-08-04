import streamlit as st


def evidencia_uploader(label: str, session_key: str, upload_key: str):
    """Widget reutilizable de carga de evidencia fotográfica.
    Usa st.file_uploader (no st.camera_input) para que en el celular el usuario
    pueda elegir directamente entre cámara nativa o galería, en un solo paso."""
    if st.session_state[session_key] is None:
        archivo = st.file_uploader(
            f"📷 {label} (abre cámara o galería en el celular)",
            type=["jpg", "jpeg", "png"],
            key=upload_key,
        )
        if archivo is not None:
            st.session_state[session_key] = archivo
            st.rerun()
        return False
    else:
        st.image(st.session_state[session_key], width=150, caption=label)
        if st.button("❌ Eliminar / Volver a adjuntar", key=f"btn_retake_{upload_key}"):
            st.session_state[session_key] = None
            st.rerun()
        return True
