(() => {
  const linkBox = document.querySelector(".link-box");
  const links = linkBox.children;

  let sequence = [...new Array(links.length).keys()];
  for (let i = links.length - 1; i > 0; i--) {
    const random = Math.floor(Math.random() * i);
    [sequence[i], sequence[random]] = [sequence[random], sequence[i]];
  }

  let innerHTML = "";
  sequence.forEach((value) => (innerHTML += links[value].outerHTML));
  linkBox.innerHTML = innerHTML;

  linkBox
    .querySelectorAll('a[href^="' + location.origin + '/go/"]')
    .forEach((a) => (a.href = atob(a.href.split("/go/").pop())));

  linkBox.querySelectorAll("img").forEach((img) => {
    for (const host of [
      "qlogo.cn",
      "zhimg.com",
      "jsdelivr.net",
      "sevencdn.com",
    ]) {
      if (img.src.includes(host)) return;
    }

    if (/avatar\/[0-9a-z]+/.test(img.src)) {
      img.src = `https://use.sevencdn.com/avatar/${
        img.src.match(/avatar\/([0-9a-z]+)/)[1]
      }?s=200`;
    }
  });
})();
