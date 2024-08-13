const Buttton = ({ text, color, onclick, size = "sm" }) => {
  const btn = document.createElement("button");
  btn.className = `btn btn-${color} btn-${size}`;
  btn.onclick = onclick;
  btn.innerText = text;
  return btn;
};
/* 
<div class="btn-group" role="group" aria-label="Basic example">
  <button type="button" class="btn btn-primary">Left</button>
  <button type="button" class="btn btn-primary">Middle</button>
  <button type="button" class="btn btn-primary">Right</button>
</div> 
*/

const ButtonGroup = ({ buttons }) => {
  const btnGroup = document.createElement("div");
  btnGroup.className = "btn-group";
  btnGroup.role = "group";
  buttons.forEach((btn) => {
    btnGroup.appendChild(Buttton(btn));
  });
  return btnGroup;
};
/* 
<div class="card bg-body-secondary ratio ratio-1x1 text-center">
    <div class="card-body">
      <div
        class="h-100 row justify-content-center align-items-center"
      >
        <div class="col-12">
          <div class="p-3"><span class="loader"></span></div>

          <button type="button" class="btn btn-primary">
            Reload
          </button>
        </div>
      </div>
    </div>
</div> 
*/

const ActionCard = ({ icon, buttons }) => {
  // Create the main card div
  const cardDiv = document.createElement("div");
  cardDiv.className = "card bg-body-secondary ratio ratio-1x1 text-center";

  // Create the card body div
  const cardBodyDiv = document.createElement("div");
  cardBodyDiv.className = "card-body";

  // Create the row div
  const rowDiv = document.createElement("div");
  rowDiv.className = "h-100 row justify-content-center align-items-center";

  // Create the col div
  const colDiv = document.createElement("div");
  colDiv.className = "col-12";

  // Create the loader div
  const loaderDiv = document.createElement("div");
  loaderDiv.className = "p-3";

  // Create the loader span
  const loaderSpan = document.createElement("span");
  loaderSpan.className = icon;

  // Append loader span to loader div
  loaderDiv.appendChild(loaderSpan);

  // Create the button
  const buttonGroup = ButtonGroup({ buttons });

  // Append loader div and button to col div
  colDiv.appendChild(loaderDiv);
  colDiv.appendChild(buttonGroup);

  // Append col div to row div
  rowDiv.appendChild(colDiv);

  // Append row div to card body div
  cardBodyDiv.appendChild(rowDiv);

  // Append card body div to card div
  cardDiv.appendChild(cardBodyDiv);

  // Append card div to the body or any other container
  return cardDiv;
};
