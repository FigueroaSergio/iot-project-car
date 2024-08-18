const IconDelete = () => {
  let IconDiv = document.createElement("div");
  IconDiv.innerHTML = `<svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                class="bi bi-trash-fill"
                viewBox="0 0 16 16"
              >
                <path
                  d="M2.5 1a1 1 0 0 0-1 1v1a1 1 0 0 0 1 1H3v9a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V4h.5a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H10a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1zm3 4a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 .5-.5M8 5a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-1 0v-7A.5.5 0 0 1 8 5m3 .5v7a.5.5 0 0 1-1 0v-7a.5.5 0 0 1 1 0"
                />
              </svg>`;
  return IconDiv;
};

const IconReload = () => {
  let IconDiv = document.createElement("div");
  IconDiv.innerHTML = ` <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                fill="currentColor"
                class="bi bi-arrow-clockwise"
                viewBox="0 0 16 16"
              >
                <path
                  fill-rule="evenodd"
                  d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"
                />
                <path
                  d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"
                />
              </svg>`;
  return IconDiv;
};
const IconDot = () => {
  let IconDiv = document.createElement("div");
  IconDiv.innerHTML = `<svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    fill="currentColor"
                    class="bi bi-circle-fill"
                    viewBox="0 0 16 16"
                  >
                    <circle cx="8" cy="8" r="8" />
                  </svg>`;
  return IconDiv;
};
const IconEye = () => {
  let IconDiv = document.createElement("div");
  IconDiv.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye-fill" viewBox="0 0 16 16">
  <path d="M10.5 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0"/>
  <path d="M0 8s3-5.5 8-5.5S16 8 16 8s-3 5.5-8 5.5S0 8 0 8m8 3.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7"/>
</svg>`;
  return IconDiv;
};
const IconRegister = {
  delete: IconDelete,
  reload: IconReload,
  dot: IconDot,
  eye: IconEye,
};

const Icon = (name) => {
  return IconRegister?.[name] ? IconRegister[name]() : null;
};

const Button = ({
  text,
  color,
  onclick,
  size = "sm",
  icon = null,
  bg = "dark-subtle",
  className = "",
}) => {
  const btn = document.createElement("button");
  btn.className = `btn bg-${bg} text-${color} btn-${size} ` + className;

  btn.type = "button";

  btn.onclick = onclick;
  let iconBtn = Icon(icon);
  if (iconBtn) {
    btn.appendChild(iconBtn);
  }
  btn.appendChild(document.createTextNode(text ?? ""));
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
    btnGroup.appendChild(Button(btn));
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

const CardConnection = ({ user, status, onDelete, onReload }) => {
  const cardDiv = document.createElement("div");
  cardDiv.className = "card p-2 mt-3";

  // Create the d-flex container div
  const dFlexDiv = document.createElement("div");
  dFlexDiv.className = "d-flex justify-content-between";

  // Create the "User" text div
  const userDiv = document.createElement("div");
  userDiv.className = "fw-bold";
  userDiv.textContent = "User";

  // Create the badge container div
  const badgeContainer = document.createElement("div");

  // Create the badge span
  const badgeSpan = document.createElement("span");
  badgeSpan.className = "badge bg-dark-subtle d-flex align-items-center";

  // Create the text-danger div for the icon
  const iconDiv = document.createElement("div");
  let colorState = "warning";
  if (status === "failed") {
    colorState = "danger";
  }
  if (status === "connected") {
    colorState = "success";
  }
  if (status === "connecting") {
    colorState = "primary";
  }

  iconDiv.className = `text-${colorState}`;

  // Create the SVG icon
  const svgIcon = IconDot();

  // Append the circle to the SVG

  // Append the SVG to the iconDiv
  iconDiv.appendChild(svgIcon);

  // Create the "New" text span
  const newSpan = document.createElement("span");
  newSpan.className = "ps-1";
  newSpan.textContent = status;

  // Append the iconDiv and newSpan to the badgeSpan
  badgeSpan.appendChild(iconDiv);
  badgeSpan.appendChild(newSpan);

  // Append the badgeSpan to the badgeContainer
  badgeContainer.appendChild(badgeSpan);

  // Append the userDiv and badgeContainer to the dFlexDiv
  dFlexDiv.appendChild(userDiv);
  dFlexDiv.appendChild(badgeContainer);

  // Create the ID text div
  const idDiv = document.createElement("div");
  idDiv.textContent = user;

  // Create the empty div with padding-top
  const paddingDiv = document.createElement("div");
  paddingDiv.className = "pt-3";
  paddingDiv.appendChild(
    Button({ icon: "delete", color: "danger", size: "md", onclick: onDelete })
  );

  paddingDiv.appendChild(
    Button({
      icon: "reload",
      color: "primary",
      size: "md",
      className: "ms-1",
      onclick: onReload,
    })
  );
  // Append the dFlexDiv, idDiv, and paddingDiv to the main cardDiv
  cardDiv.appendChild(dFlexDiv);
  cardDiv.appendChild(idDiv);
  cardDiv.appendChild(paddingDiv);
  return cardDiv;
};

const CardConnectionVideo = ({
  user,
  status,
  onDelete,
  onReload,
  onView,
  src,
}) => {
  const cardDiv = document.createElement("div");
  cardDiv.className = "card p-0 mt-2 h-100";

  let video = document.createElement("video");
  video.className = "card-img img-fluid rounded ratio ratio-1x1";
  video.autoplay = true;
  video.muted = true;
  video.volume = 0;
  video.srcObject = src;

  let over = document.createElement("div");
  over.className = "card-img-overlay bg-dark bg-opacity-75 d-flex flex-column";

  // Create the d-flex container div
  const dFlexDiv = document.createElement("div");
  dFlexDiv.className = "d-flex justify-content-between ";

  // Create the "User" text div
  const userDiv = document.createElement("div");
  userDiv.className = "fw-bold";
  userDiv.textContent = "User";

  // Create the badge container div
  const badgeContainer = document.createElement("div");

  // Create the badge span
  const badgeSpan = document.createElement("span");
  badgeSpan.className = "badge bg-dark-subtle d-flex align-items-center";

  // Create the text-danger div for the icon
  const iconDiv = document.createElement("div");
  let colorState = "warning";
  if (status === "failed") {
    colorState = "danger";
  }
  if (status === "connected") {
    colorState = "success";
  }
  if (status === "connecting") {
    colorState = "primary";
  }

  iconDiv.className = `text-${colorState}`;

  // Create the SVG icon
  const svgIcon = IconDot();

  // Append the circle to the SVG

  // Append the SVG to the iconDiv
  iconDiv.appendChild(svgIcon);

  // Create the "New" text span
  const newSpan = document.createElement("span");
  newSpan.className = "ps-1";
  newSpan.textContent = status;

  // Append the iconDiv and newSpan to the badgeSpan
  badgeSpan.appendChild(iconDiv);
  badgeSpan.appendChild(newSpan);

  // Append the badgeSpan to the badgeContainer
  badgeContainer.appendChild(badgeSpan);

  // Append the userDiv and badgeContainer to the dFlexDiv
  dFlexDiv.appendChild(userDiv);
  dFlexDiv.appendChild(badgeContainer);

  // Create the ID text div
  const idDiv = document.createElement("div");
  idDiv.textContent = user;

  // Create the empty div with padding-top
  const paddingDiv = document.createElement("div");
  paddingDiv.className = "pt-3 mt-auto";
  paddingDiv.appendChild(
    Button({ icon: "delete", color: "danger", size: "md", onclick: onDelete })
  );

  if (status !== "connected") {
    paddingDiv.appendChild(
      Button({
        icon: "reload",
        color: "primary",
        size: "md",
        className: "ms-1",
        onclick: onReload,
      })
    );
  } else {
    paddingDiv.appendChild(
      Button({
        icon: "eye",
        color: "success",
        size: "md",
        className: "ms-1",
        onclick: onView,
      })
    );
  }

  // Append the dFlexDiv, idDiv, and paddingDiv to the main cardDiv
  cardDiv.appendChild(video);
  over.appendChild(dFlexDiv);
  over.appendChild(idDiv);
  over.appendChild(paddingDiv);
  cardDiv.appendChild(over);
  return cardDiv;
};

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
