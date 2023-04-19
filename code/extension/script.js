window.addEventListener("load", function () {
  const recommendations = JSON.parse(
    localStorage.getItem("recommendationsObject")
  );
  if (recommendations) {
    updateInterface(recommendations);
  }
});

const submitBtn = document.querySelector("#submitBtn");
submitBtn.addEventListener("click", async () => {
  const historyUrls = await getHistoryUrls();
  const loading = document.querySelector("#loading");
  loading.style.display = "block";
  const recommendations = await getRecommendations(historyUrls);
  if (recommendations) {
    localStorage.setItem(
      "recommendationsObject",
      JSON.stringify(recommendations)
    );
    updateInterface(recommendations);
  }
  loading.style.display = "none";
});

async function getHistoryUrls() {
  return new Promise((resolve) => {
    chrome.history.search(
      {
        text: "",
        maxResults: 5,
        startTime: 1586997176000,
      },
      (historyItems) => {
        const historyUrls = historyItems.map((item) => item.url);
        console.log(historyUrls);
        resolve(historyUrls);
      }
    );
  });
}

async function getRecommendations(historyUrls) {
  const requestBody = JSON.stringify({ history: historyUrls });
  const response = await fetch("https://swm.rajkumaar.co.in/recommendations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: requestBody,
  });
  const responseBody = await response.json();
  return responseBody.recommendations;
}

function updateInterface(recommendations) {
  const recommendationsDiv = document.querySelector("#recommendations");
  recommendationsDiv.style.padding = "20px";
  recommendationsDiv.innerHTML =
    '<h3 class="title is-3 has-text-centered">URL Recommendations</h3>';
  const ul = document.createElement("ul");
  // ul.style.listStyleType = "auto";
  ul.className = "column is-12";

  // Loop through the recommendations and add them to the ul
  recommendations.forEach((recommendation) => {
    // Create a new li element to hold the recommendation
    const li = document.createElement("li");
    li.className = "columns is-vcentered is-mobile mb-2";

    // Add the recommendation title to the li
    const titleDiv = document.createElement("div");
    titleDiv.className = "column";
    const title = document.createElement("a");
    title.href = recommendation.url;
    title.target = "_blank";
    title.textContent = recommendation.title;
    title.className = "title is-5 mb-0";
    titleDiv.appendChild(title);
    li.appendChild(titleDiv);

    // Add the recommendation image to the li
    const imageDiv = document.createElement("div");
    imageDiv.className = "column is-3 has-text-centered";
    const image = document.createElement("img");
    image.src = recommendation.image;
    image.alt = "Thumbnail";
    image.style.maxWidth = "100px";
    image.style.maxHeight = "100px";
    imageDiv.appendChild(image);
    li.appendChild(imageDiv);

    // Add the li to the ul
    ul.appendChild(li);
  });

  recommendationsDiv.appendChild(ul);
  recommendationsDiv.classList.remove("is-hidden");
}
