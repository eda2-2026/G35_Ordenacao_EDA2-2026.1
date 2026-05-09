document.addEventListener('DOMContentLoaded', function () {
    const userIcon = document.getElementById('user-icon');
    const userPopup = document.getElementById('user-popup');
    const editProfileLink = document.getElementById('edit-profile-link');

    // Função para abrir/fechar o popup ao clicar no ícone de usuário
    userIcon.addEventListener('click', function (event) {
        userPopup.style.display = userPopup.style.display === 'block' ? 'none' : 'block';
    });

    // Fechar o popup se o usuário clicar fora dele
    document.addEventListener('click', function (event) {
        if (!userPopup.contains(event.target) && !userIcon.contains(event.target)) {
            userPopup.style.display = "none";
        }
    });

    // Redirecionamento ao clicar em "Editar Perfil"
    if (editProfileLink) {
        const isSuperuser = userPopup.getAttribute('data-is-superuser') === 'True';  
        editProfileLink.addEventListener('click', function (event) {
            event.preventDefault();  
            if (isSuperuser) {
                window.location.href = "/admin";  
            } else {
                window.location.href = "/adm";    
            }
        });
    }
});
