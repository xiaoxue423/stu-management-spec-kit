import { describe, expect, it } from "vitest";

import {
  GENDER_LABELS,
  GENDER_OPTIONS,
  MONTH_OPTIONS,
  SUBJECT_LABELS,
  SUBJECT_OPTIONS,
  toGenderLabel,
} from "../../src/types/student";

describe("enum options guard", () => {
  it("keeps gender options limited to male/female", () => {
    expect(GENDER_OPTIONS).toEqual(["male", "female"]);
  });

  it("keeps month options within 1-12", () => {
    expect(MONTH_OPTIONS[0]).toBe(1);
    expect(MONTH_OPTIONS[MONTH_OPTIONS.length - 1]).toBe(12);
  });

  it("keeps subject options limited to three subjects", () => {
    expect(SUBJECT_OPTIONS).toEqual(["math", "chinese", "english"]);
  });

  it("uses Chinese labels for gender display", () => {
    expect(GENDER_LABELS.male).toBe("男");
    expect(GENDER_LABELS.female).toBe("女");
    expect(toGenderLabel("male")).toBe("男");
  });

  it("uses Chinese labels for subjects display", () => {
    expect(SUBJECT_LABELS.math).toBe("数学");
    expect(SUBJECT_LABELS.chinese).toBe("语文");
    expect(SUBJECT_LABELS.english).toBe("英语");
  });
});
