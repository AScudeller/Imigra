document.addEventListener('DOMContentLoaded', function () {
    function applyMask(input) {
        if (!input) return;

        input.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) value = value.slice(0, 10);

            let formatted = '';
            if (value.length > 0) {
                formatted = '(' + value.substring(0, 3);
                if (value.length > 3) {
                    formatted += ') ' + value.substring(3, 6);
                    if (value.length > 6) {
                        formatted += '-' + value.substring(6, 10);
                    }
                }
            }

            e.target.value = formatted;
        });

        // Aplicar máscara inicial
        if (input.value) {
            let value = input.value.replace(/\D/g, '');
            if (value.length === 10) {
                input.value = '(' + value.substring(0, 3) + ') ' + value.substring(3, 6) + '-' + value.substring(6, 10);
            }
        }
    }

    // Função para observar novos elementos (inlines dinâmicos)
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element
                    const phoneInputs = node.querySelectorAll('input[id$="telefone"], input[id$="whatsapp"]');
                    phoneInputs.forEach(applyMask);
                }
            });
        });
    });

    // Iniciar nos campos existentes
    const existingInputs = document.querySelectorAll('input[id$="telefone"], input[id$="whatsapp"]');
    existingInputs.forEach(applyMask);

    // Observar mudanças no corpo do admin para capturar inlines adicionados
    const adminContent = document.getElementById('content-main') || document.body;
    observer.observe(adminContent, { childList: true, subtree: true });
});
