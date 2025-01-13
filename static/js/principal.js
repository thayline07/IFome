const barraDePesquisa = document.querySelector('#barra-de-pesquisa');

barraDePesquisa.addEventListener("input", filtrarPesquisa);

function filtrarPesquisa() {
    const produtos = document.querySelectorAll('.produto');
    const valorPesquisa = barraDePesquisa.value.toLowerCase();

    produtos.forEach(produto => {
        let titulo = produto.querySelector('.produto-nome').textContent.toLowerCase();

        if (titulo.includes(valorPesquisa) || valorPesquisa === "") {
            produto.style.display = "flex";
        } else {
            produto.style.display = "none";
        }
    })
}