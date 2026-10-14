(function (root, factory) {
  const api = factory();

  if (typeof module === "object" && module.exports) {
    module.exports = api;
  }

  if (root && root.document) {
    root.addEventListener("DOMContentLoaded", function () {
      api.initializePickPen(root.document);
    });
  }
})(typeof window !== "undefined" ? window : undefined, function () {
  "use strict";

  function normalizeText(value) {
    return String(value || "")
      .toLocaleLowerCase()
      .trim()
      .replace(/\s+/g, " ");
  }

  function matchesPick(record, filters) {
    const query = normalizeText(filters.query);
    const showMatches = !filters.show || record.shows.includes(filters.show);
    const licenseMatches =
      !filters.license ||
      (filters.license === "__unknown__" ? !record.license : record.license === filters.license);
    const searchMatches = !query || normalizeText(record.search).includes(query);

    return showMatches && licenseMatches && searchMatches;
  }

  function compareTitles(left, right) {
    return left.title.localeCompare(right.title, undefined, { sensitivity: "base" });
  }

  function comparatorFor(sortValue) {
    if (sortValue === "title-desc") {
      return function (left, right) {
        return compareTitles(right, left);
      };
    }

    if (sortValue === "date-desc") {
      return function (left, right) {
        return right.timestamp - left.timestamp || compareTitles(left, right);
      };
    }

    return compareTitles;
  }

  function parseShows(value) {
    try {
      const shows = JSON.parse(value || "[]");
      return Array.isArray(shows) ? shows : [];
    } catch (_error) {
      return [];
    }
  }

  function initializePickPen(document) {
    const controls = document.querySelector("#pick-discovery-controls");
    const grid = document.querySelector("#pick-grid");

    if (!controls || !grid) {
      return;
    }

    const search = controls.querySelector("#pick-search");
    const show = controls.querySelector("#pick-show");
    const license = controls.querySelector("#pick-license");
    const sort = controls.querySelector("#pick-sort");
    const reset = controls.querySelector("#pick-reset");
    const count = document.querySelector("#pick-results-count");
    const emptyState = document.querySelector("#pick-empty-state");

    const records = Array.from(grid.querySelectorAll(".pick.card")).map(function (element) {
      return {
        element: element,
        title: element.dataset.title || "",
        search: element.dataset.search || "",
        shows: parseShows(element.dataset.shows),
        license: element.dataset.license || "",
        timestamp: Number(element.dataset.featuredTimestamp || 0),
      };
    });

    function render() {
      const filters = {
        query: search.value,
        show: show.value,
        license: license.value,
      };
      const visibleRecords = records.filter(function (record) {
        return matchesPick(record, filters);
      });
      const sortedRecords = [...records].sort(comparatorFor(sort.value));

      sortedRecords.forEach(function (record) {
        record.element.hidden = !visibleRecords.includes(record);
        grid.appendChild(record.element);
      });

      const resultCount = visibleRecords.length;
      count.textContent = resultCount + (resultCount === 1 ? " pick" : " picks");
      emptyState.hidden = resultCount !== 0;
    }

    search.addEventListener("input", render);
    show.addEventListener("change", render);
    license.addEventListener("change", render);
    sort.addEventListener("change", render);
    reset.addEventListener("click", function () {
      controls.reset();
      render();
      search.focus();
    });

    controls.hidden = false;
    render();
  }

  return {
    comparatorFor: comparatorFor,
    initializePickPen: initializePickPen,
    matchesPick: matchesPick,
    normalizeText: normalizeText,
  };
});
