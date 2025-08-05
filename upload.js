const uploadForm = document.getElementById("uploadForm");
const resultDiv = document.getElementById("result");
const limitMessage = document.getElementById("limit-message");

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = document.getElementById("file").files[0];
  const email = document.getElementById("email").value;

  if (!file || !email) {
    alert("Пожалуйста, заполните все поля");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("email", email);

  try {
    const response = await fetch("https://analytic-bot2.onrender.com", {
      method: "POST",
      body: formData
    });

    if (response.status === 403) {
      limitMessage.classList.remove("hidden");
      return;
    }

    if (!response.ok) {
      throw new Error("Ошибка при анализе отчёта");
    }

    const data = await response.json();
    resultDiv.innerHTML = `<h3>Результат анализа:</h3><p>${data.result}</p>`;
  } catch (error) {
    resultDiv.innerHTML = `<p style="color:red;">Ошибка: ${error.message}</p>`;
  }
});
