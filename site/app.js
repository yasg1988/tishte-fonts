const sample = document.querySelector('#sample');
const family = document.querySelector('#font-family');
const weight = document.querySelector('#font-weight');
const size = document.querySelector('#font-size');
const italic = document.querySelector('#font-italic');
const sizeOutput = document.querySelector('#size-output');

function updateSample() {
  sample.className = `editable ${family.value}`;
  sample.style.fontWeight = weight.value;
  sample.style.fontSize = `${size.value}px`;
  sample.style.fontStyle = italic.checked ? 'italic' : 'normal';
  sizeOutput.value = `${size.value} px`;
}

[family, weight, size, italic].forEach((control) => {
  control.addEventListener('input', updateSample);
});

updateSample();
