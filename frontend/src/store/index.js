// store/index.js
import { createStore } from 'vuex';

const groupRepeatedUnits = (templateUnitArray = [{ unit: "1fr" }]) => {
  const templateArray = templateUnitArray.map(i => i["unit"]);
  const groups = [[templateArray.shift()]];
  for (const templateUnit of templateArray) {
    const lastGroup = groups[groups.length - 1];
    if (lastGroup.indexOf(templateUnit) !== -1) {
      lastGroup.push(templateUnit);
    } else {
      groups.push([templateUnit]);
    }
  }
  return groups;
};

const createRepetition = (groups, maxRepetition = 1) => {
  return groups
    .map(group =>
      // If you want to add repetition only when a measure is repeated more than x times,
      // change maxRepetition value to x
      group.length === maxRepetition
        ? group.join(" ")
        : `repeat(${group.length}, ${group[0]})`
    )
    .join(" ");
};

export default createStore({
  state: {
    columns: 5,
    rows: 5,
    columngap: 0,
    rowgap: 0,
    colArr: [],
    rowArr: [],
    childarea: []
  },
  getters: {
    colTemplate(state) {
      const unitGroups = groupRepeatedUnits(state.colArr);
      return createRepetition(unitGroups);
    },
    rowTemplate(state) {
      const unitGroups = groupRepeatedUnits(state.rowArr);
      return createRepetition(unitGroups);
    },
    divNum(state) {
      return Math.max(state.columns, 0) * Math.max(state.rows, 0);
    }
  },
  mutations: {
    initialArrIndex(state, payload) {
      if(payload !== '') {
        const queryParams = new URLSearchParams(payload)

        for (const stateKey in state) {
          const paramIsValid = queryParams.has(stateKey)
          const paramType = typeof(state[stateKey])

          if(paramIsValid && paramType === 'number') {
            state[stateKey] = queryParams.get(stateKey);
          }
          else if (paramIsValid && paramType === 'object') {
            state[stateKey] = JSON.parse(queryParams.get(stateKey))
          }
        }
      } else {
          createArr(state.columns, state.colArr);
          createArr(state.rows, state.rowArr);
      }
    },
    adjustArr(state, payload) {
      let newVal = Math.max(Number(payload.newVal), 0),
        oldVal = Math.max(Number(payload.oldVal), 0);

      if (newVal < oldVal) {
        // you'd think that .length would be quicker here, but it doesn't trigger the getter/computed in colTemplate etc.
        let difference = oldVal - newVal;
        for (let i = 1; i <= difference; i++) {
          state[payload.direction].pop();
        }
      } else {
        let difference = newVal - oldVal;
        for (let i = 1; i <= difference; i++) {
          state[payload.direction].push({ unit: "1fr" });
        }
      }
    },
    addChildren(state, payload) {
      state.childarea.push(payload);
    },
    removeChildren(state, payload) {
      state.childarea.splice(payload, 1);
    },
    updateColumns(state, payload) {
      state.columns = payload;
    },
    updateRows(state, payload) {
      state.rows = payload;
    },
    updateColumnGap(state, payload) {
      state.columngap = payload;
    },
    updateRowGap(state, payload) {
      state.rowgap = payload;
    },
    resetGrid(state, payload) {
      state.childarea = [];
    }
  }
});

//we start off with just a few rows and columns filled with 1fr units
const createArr = (direction, arr) => {
  for (let i = 1; i <= direction; i++) {
    arr.push({ unit: "1fr" });
  }
};