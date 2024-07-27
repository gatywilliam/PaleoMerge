export async function import_data(path: string) {
  const data = await fetch('http://localhost:5000/import?path=' + path);
  return data.json();
}

export async function update_data() {
  const data = await fetch('http://localhost:5000/update');
  return data.json();
}

export async function save_data() {
  const data = await fetch('http://localhost:5000/save');
  return data.json();
}

export async function save_data_as(path: string) {
  const data = await fetch('http://localhost:5000/save-as?path=' + path);
  return data.json();
}
