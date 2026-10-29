(() => {
  "use strict";

  const MAX_CONSTRAINTS = 4;
  const MIN_OPTIONS = 3;
  const MAX_OPTIONS = 5;
  const OPTION_LETTERS = ["A", "B", "C", "D", "E"];
  const CONSENT_KEYS = ["tanpa_ai", "data_pribadi", "sara_medis_hukum", "bukan_salinan", "lisensi_cc_by"];
  const GENERIC_NETWORK_ERROR = "Gagal mengirim. Periksa koneksi lalu coba lagi.";

  const form = document.getElementById("form");
  const submitButton = document.getElementById("submit");
  const summary = document.getElementById("summary");
  const result = document.getElementById("result");

  let catalog = null;

  // ---------- kecil ----------

  function $(id) {
    return document.getElementById(id);
  }

  function el(tag, attrs, ...children) {
    const node = document.createElement(tag);
    const options = attrs || {};
    for (const [key, value] of Object.entries(options)) {
      if (value === undefined || value === null || value === false) continue;
      if (key === "text") node.textContent = String(value);
      else if (key === "class") node.className = String(value);
      else if (value === true) node.setAttribute(key, "");
      else node.setAttribute(key, String(value));
    }
    for (const child of children) {
      if (child !== null && child !== undefined) node.append(child);
    }
    return node;
  }

  function val(id) {
    const node = $(id);
    return node ? node.value.trim() : "";
  }

  function numOrNull(id) {
    const raw = val(id);
    if (raw === "") return null;
    const n = Number(raw);
    return Number.isNaN(n) ? raw : n;
  }

  function checkedValue(name) {
    const node = document.querySelector(`input[name="${name}"]:checked`);
    return node ? node.value : "";
  }

  function errorNode(key) {
    return document.querySelector(`[data-err="${CSS.escape(key)}"]`);
  }

  function controlFor(key) {
    return document.querySelector(`[data-field="${CSS.escape(key)}"]`);
  }

  function fillSelect(select, items, placeholder) {
    select.replaceChildren(
      el("option", { value: "", text: placeholder }),
      ...items.map((item) => el("option", { value: item.id, text: item.label })),
    );
  }

  function renderRadios(container, name, items, selectedId) {
    container.replaceChildren(
      ...items.map((item) => {
        const id = `${name}-${item.id}`;
        const input = el("input", { type: "radio", name, id, value: item.id });
        input.checked = item.id === selectedId;
        return el(
          "div",
          { class: "choice-row" },
          input,
          el(
            "label",
            { for: id },
            el("span", { class: "choice-title", text: item.label }),
            item.desc ? el("span", { class: "choice-desc", text: item.desc }) : null,
          ),
        );
      }),
    );
  }

  // ---------- error dan ringkasan ----------

  function clearErrors() {
    document.querySelectorAll("[data-err]").forEach((node) => {
      node.textContent = "";
      node.hidden = true;
    });
    document.querySelectorAll("[aria-invalid]").forEach((node) => node.removeAttribute("aria-invalid"));
    summary.hidden = true;
    summary.replaceChildren();
    result.hidden = true;
    result.replaceChildren();
  }

  function fieldLabel(key, control) {
    if (key.startsWith("consent_")) return "Persetujuan";
    if (control.tagName === "FIELDSET") {
      const legend = control.querySelector(":scope > legend");
      return legend ? legend.textContent.trim() : "";
    }
    const label = control.id ? document.querySelector(`label[for="${CSS.escape(control.id)}"]`) : null;
    return label ? label.textContent.trim() : "";
  }

  function showErrors(errors) {
    const entries = Object.entries(errors);
    if (entries.length === 0) return;

    const items = [];
    for (const [key, message] of entries) {
      const node = errorNode(key);
      if (node) {
        node.textContent = message;
        node.hidden = false;
      }
      const control = controlFor(key);
      if (control) {
        control.setAttribute("aria-invalid", "true");
        if (!control.id) control.id = `f-${key}`;
        const label = fieldLabel(key, control);
        const text = label ? `${label}: ${message}` : message;
        items.push(el("li", null, el("a", { href: `#${control.id}`, text })));
      } else {
        items.push(el("li", { text: message }));
      }
    }

    summary.replaceChildren(
      el("p", { text: `Ada ${entries.length} hal yang perlu diperbaiki:` }),
      el("ul", null, ...items),
    );
    summary.hidden = false;
    summary.focus();
  }

  // ---------- baris dinamis ----------

  function readConstraintRows() {
    const selects = document.querySelectorAll("#constraint-rows select");
    return Array.from(selects, (select, i) => ({
      type: select.value,
      note: $(`constraint_${i}_note`).value.trim(),
    }));
  }

  function renderConstraintRows(rows) {
    const box = $("constraint-rows");
    box.replaceChildren(
      ...rows.map((row, i) => {
        const selectId = `constraint_${i}`;
        const noteId = `constraint_${i}_note`;

        const select = el("select", { id: selectId, "data-field": selectId });
        fillSelect(select, [], "Pilih jenis constraint");
        for (const c of catalog.constraints) {
          select.append(el("option", { value: c.type, text: `${c.label} (contoh: "${c.example}")` }));
        }
        select.value = row.type || "";

        const note = el("input", { type: "text", id: noteId, "data-field": noteId, maxlength: "200", autocomplete: "off" });
        note.value = row.note || "";

        const removeButton = rows.length > 1
          ? el("button", { type: "button", class: "btn-link", "data-remove-constraint": i, text: `Hapus constraint ${i + 1}` })
          : null;

        return el(
          "div",
          { class: "subcard" },
          el(
            "div",
            { class: "field" },
            el("label", { for: selectId, text: `Jenis constraint ${i + 1}` }),
            select,
            el("p", { class: "err", "data-err": selectId, hidden: true }),
          ),
          el(
            "div",
            { class: "field" },
            el("label", { for: noteId, text: "Keterangan (opsional)" }),
            note,
            el("p", { class: "hint", text: "Contoh: maksimal 40 kata" }),
            el("p", { class: "err", "data-err": noteId, hidden: true }),
          ),
          removeButton,
        );
      }),
    );
    $("add-constraint").disabled = rows.length >= MAX_CONSTRAINTS;
  }

  function readOptions() {
    return Array.from(document.querySelectorAll("#opsi-list input"), (input) => input.value.trim());
  }

  function renderOptions(values) {
    const list = $("opsi-list");
    list.replaceChildren(
      ...values.map((value, i) => {
        const id = `opsi_${i}`;
        const input = el("input", { type: "text", id, "data-field": id, maxlength: "200", autocomplete: "off" });
        input.value = value || "";
        return el(
          "div",
          { class: "field" },
          el("label", { for: id, text: `Pilihan ${OPTION_LETTERS[i]}` }),
          input,
          el("p", { class: "err", "data-err": id, hidden: true }),
        );
      }),
    );
    $("add-opsi").disabled = values.length >= MAX_OPTIONS;
    $("remove-opsi").disabled = values.length <= MIN_OPTIONS;
    refreshKunci();
  }

  function refreshKunci() {
    const select = $("kunci");
    const previous = select.value;
    const count = document.querySelectorAll("#opsi-list input").length;
    const letters = OPTION_LETTERS.slice(0, count);
    select.replaceChildren(
      el("option", { value: "", text: "Pilih jawaban yang benar" }),
      ...letters.map((letter) => el("option", { value: letter, text: letter })),
    );
    select.value = letters.includes(previous) ? previous : "";
  }

  // ---------- tampilan per jenis soal ----------

  function showPanelFor(type) {
    document.querySelectorAll("[data-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.panel !== type;
    });
  }

  function syncFormat() {
    const format = checkedValue("format");
    $("block-pilihan_ganda").hidden = format !== "pilihan_ganda";
    $("block-jawaban_singkat").hidden = format !== "jawaban_singkat";
  }

  function syncPartner() {
    $("partner-lain-wrap").hidden = $("partner").value !== "Lainnya";
  }

  function updateCounter(input) {
    const max = Number(input.dataset.max);
    const counter = $(`${input.id}-count`);
    if (counter && max) counter.textContent = `${input.value.length} / ${max}`;
  }

  function randomPseudonym() {
    const bytes = new Uint32Array(1);
    crypto.getRandomValues(bytes);
    return `penulis_${String(bytes[0] % 10000).padStart(4, "0")}`;
  }

  // ---------- payload ----------

  function buildPayload() {
    const type = checkedValue("item_type");
    const payload = {
      item_type: type,
      pseudonim: val("pseudonim"),
      partner: val("partner"),
      partner_lain: val("partner_lain"),
      email: val("email"),
      website: val("website"),
      consent: Object.fromEntries(CONSENT_KEYS.map((key) => [key, $(`consent_${key}`).checked])),
    };

    if (type === "instruksi") {
      Object.assign(payload, {
        prompt: val("prompt"),
        register: checkedValue("register"),
        topic: val("topic"),
        constraints: readConstraintRows(),
        reference_response: val("reference_response"),
      });
    } else if (type === "pengetahuan") {
      const format = checkedValue("format");
      Object.assign(payload, {
        pertanyaan: val("pertanyaan"),
        bidang: val("bidang"),
        provinsi: val("provinsi"),
        tingkat: val("tingkat"),
        format,
        sumber: val("sumber"),
        penjelasan: val("penjelasan"),
      });
      if (format === "pilihan_ganda") {
        payload.opsi = readOptions();
        payload.kunci = val("kunci");
      } else if (format === "jawaban_singkat") {
        payload.kunci_jawaban = val("kunci_jawaban");
        payload.varian = $("varian").value;
      }
    } else if (type === "sastra") {
      Object.assign(payload, {
        jenis: val("jenis"),
        tugas: val("tugas"),
        jumlah_bait: numOrNull("jumlah_bait"),
        baris_per_bait: numOrNull("baris_per_bait"),
        pola_rima: val("pola_rima"),
        suku_kata_min: numOrNull("suku_kata_min"),
        suku_kata_max: numOrNull("suku_kata_max"),
        kriteria_penilaian: val("kriteria_penilaian"),
        contoh_jawaban: val("contoh_jawaban"),
        sumber_contoh: val("sumber_contoh"),
      });
    }
    return payload;
  }

  // ---------- reset setelah berhasil (data penulis tetap) ----------

  function resetItemFields() {
    const writer = {
      pseudonim: val("pseudonim"),
      partner: $("partner").value,
      partner_lain: val("partner_lain"),
      email: val("email"),
    };
    const type = checkedValue("item_type") || "instruksi";

    form.reset();
    $("pseudonim").value = writer.pseudonim;
    $("partner").value = writer.partner;
    $("partner_lain").value = writer.partner_lain;
    $("email").value = writer.email;
    syncPartner();

    renderRadios($("item-type-options"), "item_type", catalog.item_types, type);
    renderRadios($("register-options"), "register", catalog.registers, null);
    renderRadios($("format-options"), "format", catalog.formats, "pilihan_ganda");
    renderConstraintRows([{ type: "", note: "" }]);
    renderOptions(["", "", ""]);
    showPanelFor(type);
    syncFormat();
    document.querySelectorAll("[data-max]").forEach(updateCounter);
  }

  // ---------- kirim ----------

  async function onSubmit(event) {
    event.preventDefault();
    clearErrors();
    submitButton.disabled = true;
    const previousLabel = submitButton.textContent;
    submitButton.textContent = "Mengirim...";

    let response = null;
    let data = null;
    try {
      response = await fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(buildPayload()),
      });
      data = await response.json().catch(() => null);
    } catch (error) {
      showErrors({ _form: GENERIC_NETWORK_ERROR });
      submitButton.disabled = false;
      submitButton.textContent = previousLabel;
      return;
    }

    submitButton.disabled = false;
    submitButton.textContent = previousLabel;

    if (data && data.ok) {
      result.replaceChildren(
        el("p", { text: "Soal kamu sudah diterima. Terima kasih." }),
        el("p", { text: `Nomor soal: ${data.submission_id}. Simpan nomor ini untuk referensi.` }),
      );
      result.hidden = false;
      resetItemFields();
      result.focus();
      return;
    }
    if (data && data.errors) {
      showErrors(data.errors);
      return;
    }
    showErrors({ _form: "Ada gangguan di server. Coba lagi beberapa saat lagi." });
  }

  // ---------- panduan: tabel constraint ----------

  function renderConstraintTable() {
    const categoryLabel = Object.fromEntries(catalog.categories.map((c) => [c.id, c.label]));
    $("constraint-table").replaceChildren(
      ...catalog.constraints.map((c) =>
        el(
          "tr",
          null,
          el("td", { text: `${c.category}. ${categoryLabel[c.category]}` }),
          el("td", { text: c.label }),
          el("td", { text: c.type }),
          el("td", { text: `"${c.example}"` }),
        ),
      ),
    );
  }

  // ---------- inisialisasi ----------

  function bindEvents() {
    form.addEventListener("submit", onSubmit);

    $("acak").addEventListener("click", () => {
      $("pseudonim").value = randomPseudonym();
    });

    $("partner").addEventListener("change", syncPartner);

    form.addEventListener("change", (event) => {
      if (event.target.name === "item_type") showPanelFor(event.target.value);
      if (event.target.name === "format") syncFormat();
    });

    $("add-constraint").addEventListener("click", () => {
      const rows = readConstraintRows();
      if (rows.length < MAX_CONSTRAINTS) {
        rows.push({ type: "", note: "" });
        renderConstraintRows(rows);
      }
    });

    $("constraint-rows").addEventListener("click", (event) => {
      const button = event.target.closest("[data-remove-constraint]");
      if (!button) return;
      const index = Number(button.dataset.removeConstraint);
      const rows = readConstraintRows();
      rows.splice(index, 1);
      renderConstraintRows(rows);
    });

    $("add-opsi").addEventListener("click", () => {
      const values = readOptions();
      if (values.length < MAX_OPTIONS) {
        values.push("");
        renderOptions(values);
      }
    });

    $("remove-opsi").addEventListener("click", () => {
      const values = readOptions();
      if (values.length > MIN_OPTIONS) {
        values.pop();
        renderOptions(values);
      }
    });

    document.querySelectorAll("[data-max]").forEach((input) => {
      input.addEventListener("input", () => updateCounter(input));
      updateCounter(input);
    });
  }

  function fillStaticSelects() {
    fillSelect($("partner"), [
      ...catalog.partners.map((p) => ({ id: p, label: p })),
      { id: catalog.partner_other, label: `${catalog.partner_other} (tulis sendiri)` },
    ], "Pilih");
    fillSelect($("topic"), catalog.topics, "Pilih topik");
    fillSelect($("bidang"), catalog.bidang, "Pilih bidang");
    fillSelect($("tingkat"), catalog.tingkat, "Pilih tingkat");
    fillSelect($("jenis"), catalog.jenis_sastra, "Pilih jenis karya");
  }

  function buildDynamicParts() {
    fillStaticSelects();
    renderRadios($("item-type-options"), "item_type", catalog.item_types, "instruksi");
    renderRadios($("register-options"), "register", catalog.registers, null);
    renderRadios($("format-options"), "format", catalog.formats, "pilihan_ganda");
    renderConstraintRows([{ type: "", note: "" }]);
    renderOptions(["", "", ""]);
    renderConstraintTable();
    showPanelFor(checkedValue("item_type") || "instruksi");
    syncFormat();
    syncPartner();
  }

  async function init() {
    bindEvents();
    try {
      const response = await fetch("/api/catalog", { headers: { Accept: "application/json" } });
      if (!response.ok) throw new Error(`catalog ${response.status}`);
      catalog = await response.json();
      buildDynamicParts();
    } catch (error) {
      showErrors({ _form: "Daftar pilihan gagal dimuat. Muat ulang halaman lalu coba lagi." });
      submitButton.disabled = true;
    }
  }

  init();
})();
