// Testi za kodiranje/dekodiranje permalinka (issue #7). Poženi z: node testi/test_permalink.js
const assert = require("assert");
const { zakodiraj, odkodiraj } = require("../out/permalink.js");

const testi = {
  "vse izbrano se ne zapise": () => {
    assert.strictEqual(zakodiraj([{ razred: "program", izbrani: ["a", "b"], neizbrani: [] }]), "");
  },

  "manj izbranih kot preskocenih -> nastejemo izbrane": () => {
    assert.strictEqual(
      zakodiraj([{ razred: "program", izbrani: ["1Mate"], neizbrani: ["2PeMa", "1ApMa"] }]),
      "program=1Mate"
    );
  },

  "vec izbranih kot preskocenih -> nastejemo preskocene": () => {
    assert.strictEqual(
      zakodiraj([{ razred: "program", izbrani: ["a", "b", "c"], neizbrani: ["2PeMa"] }]),
      "program-skip=2PeMa"
    );
  },

  "pri izenacenju nastejemo izbrane": () => {
    assert.strictEqual(
      zakodiraj([{ razred: "letnik", izbrani: ["prvi"], neizbrani: ["drugi"] }]),
      "letnik=prvi"
    );
  },

  "nic izbranega": () => {
    assert.strictEqual(
      zakodiraj([{ razred: "rok", izbrani: [], neizbrani: ["1.", "2."] }]),
      "rok="
    );
  },

  "vec skupin locimo z &": () => {
    assert.strictEqual(
      zakodiraj([
        { razred: "program", izbrani: ["1Mate"], neizbrani: ["2PeMa"] },
        { razred: "letnik", izbrani: ["prvi"], neizbrani: ["drugi"] },
      ]),
      "program=1Mate&letnik=prvi"
    );
  },

  "imena s presledki, vejicami in sumniki so ubezana": () => {
    const niz = zakodiraj([
      { razred: "predmet", izbrani: ["Uvod v programiranje", "A, B"], neizbrani: ["x", "y", "z"] },
    ]);
    assert.ok(!niz.includes(" "), "presledkov ne sme biti: " + niz);
    assert.deepStrictEqual(odkodiraj(niz).predmet.imena, ["Uvod v programiranje", "A, B"]);
  },

  "odkodiraj prazen niz": () => {
    assert.deepStrictEqual(odkodiraj(""), {});
  },

  "odkodiraj prepozna -skip": () => {
    assert.deepStrictEqual(odkodiraj("program-skip=2PeMa"), {
      program: { preskoci: true, imena: ["2PeMa"] },
    });
  },

  "odkodiraj prazno vrednost kot prazen seznam": () => {
    assert.deepStrictEqual(odkodiraj("rok="), { rok: { preskoci: false, imena: [] } });
  },

  "odkodiraj ignorira smeti": () => {
    assert.deepStrictEqual(odkodiraj("&&nekaj&program=1Mate&"), {
      program: { preskoci: false, imena: ["1Mate"] },
    });
  },

  "krozna pot": () => {
    const skupine = [
      { razred: "program", izbrani: ["1Mate", "magistrski študij"], neizbrani: ["2PeMa", "1ApMa", "1FiMa"] },
      { razred: "izvajalec", izbrani: ["a", "b", "c"], neizbrani: ["Šestković Matej"] },
    ];
    const odkodirano = odkodiraj(zakodiraj(skupine));
    assert.deepStrictEqual(odkodirano.program, { preskoci: false, imena: ["1Mate", "magistrski študij"] });
    assert.deepStrictEqual(odkodirano.izvajalec, { preskoci: true, imena: ["Šestković Matej"] });
  },
};

let padli = 0;
for (const [ime, test] of Object.entries(testi)) {
  try {
    test();
    console.log("  ok   " + ime);
  } catch (e) {
    padli++;
    console.log("  NAPAKA " + ime + ": " + e.message);
  }
}
console.log(padli === 0 ? `\nvseh ${Object.keys(testi).length} testov je uspelo` : `\n${padli} testov ni uspelo`);
process.exit(padli === 0 ? 0 : 1);
