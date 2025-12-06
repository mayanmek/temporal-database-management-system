function waitForPywebview(callback) {
    if (window.pywebview) {
        setTimeout(callback, 50);
    } else {
        setTimeout(() => waitForPywebview(callback), 50);
    }
}


async function main()
{
    document.body.style.userSelect = 'text';
    document.body.onselectstart = null;

    const actionSelect = document.getElementById('actionSelect');
    const resultFields = document.getElementById('resultFields');
    const historyFields = document.getElementById('historyFields');
    const newValueRow = document.getElementById('newValueRow');

    // generic
    const firstNameInput = document.getElementById('firstName');
    const lastNameInput = document.getElementById('lastName');
    const loincNumberInput = document.getElementById('loincNumber');

    // Dynamic Fields - Get Result / Update / Delete
    const validDateInput = document.getElementById('validDate');
    const validTimeInput = document.getElementById('validTime');
    const currDateInput = document.getElementById('CurrDate');
    const currTimeInput = document.getElementById('CurrTime');
    const newValueInput = document.getElementById('newValue'); // Update only

    // Dynamic Fields - Get History
    const validDateHistInput = document.getElementById('validDateHist');
    const validTimeHistInput = document.getElementById('validTimeHist');
    const startDateInput = document.getElementById('startDate');
    const startTimeInput = document.getElementById('startTime');
    const endDateInput = document.getElementById('endDate');
    const endTimeInput = document.getElementById('endTime');


    // output
    const errorMsg = document.getElementById('errorMessage');
    const message = document.getElementById('message');
    const table = document.getElementById('myTable');
    const tableHeaders = document.getElementById('tableHeaders');
    const tableData = document.getElementById('tableData');

    actionSelect.addEventListener('change', () => {
      const value = actionSelect.value;
      resultFields.style.display = 'none';
      historyFields.style.display = 'none';
      newValueRow.style.display = 'none';

      if (value === 'get_result' || value === 'delete') {
        resultFields.style.display = 'block';
      } else if (value === 'update') {
        resultFields.style.display = 'block';
        newValueRow.style.display = 'block';
      } else if (value === 'get_history') {
        historyFields.style.display = 'block';
      }
    });
    fnameList = document.getElementById("fnameList");
    fnames = await pywebview.api.get_fnames();
    fnameList.append(...fnames.map(name => {
        const opt = document.createElement("option");
        opt.value = name;
        return opt;
    }));

    lnameList = document.getElementById("lnameList");
    lnames = await pywebview.api.get_lnames();
    lnameList.append(...lnames.map(name => {
        const opt = document.createElement("option");
        opt.value = name;
        return opt;
    }));

    loincList = document.getElementById("loincList");
    loincs = await pywebview.api.get_loinc();
    loincList.append(...loincs.map(loinc => {
        const opt = document.createElement("option");
        opt.value = loinc;
        return opt;
    }));

    document.getElementById("submitBtn").addEventListener("click", async () => {
        const selectedAction = actionSelect.value;
        let data = null;
        switch (selectedAction) {
            case "get_result":
                data = await pywebview.api.get_result(
                        firstNameInput.value, lastNameInput.value, loincNumberInput.value,
                        validDateInput.value, validTimeInput.value,
                        currDateInput.value, currTimeInput.value
                )
                break;
            case "get_history":
                data = await pywebview.api.get_history(
                        firstNameInput.value, lastNameInput.value, loincNumberInput.value,
                        validDateHistInput.value, validTimeHistInput.value,
                        startDateInput.value, startTimeInput.value,
                        endDateInput.value, endTimeInput.value
                )
                break;
            case "update":
                data = await pywebview.api.update(
                        firstNameInput.value, lastNameInput.value, loincNumberInput.value,
                        validDateInput.value, validTimeInput.value,
                        currDateInput.value, currTimeInput.value,
                        newValue.value
                )
                break;
            case "delete":
                data = await pywebview.api.delete(
                        firstNameInput.value, lastNameInput.value, loincNumberInput.value,
                        validDateInput.value, validTimeInput.value,
                        currDateInput.value, currTimeInput.value
                )
                break;
            default:
                console.error("Unknown action:", selectedAction);
                return;
            }
            errorMsg.classList.add("d-none");
            message.classList.add("d-none");
            table.classList.add("d-none");
            if(data.status == "error")
            {
                errorMsg.classList.remove("d-none");
                errorMsg.textContent = data.message;
            }
            else
            {
                message.classList.remove("d-none");
                message.textContent = data.message;
                if(data.data)
                {
                      table.classList.remove("d-none");
                      // Clear existing rows in the table body and headers using replaceChildren
                      tableData.replaceChildren();  // Clears all child nodes (rows) in the body
                      tableHeaders.replaceChildren(); // Clears all header cells (th)

                      // Add headers to the table
                      data.data.headers.forEach((header, index) => {
                        const th = document.createElement('th');
                        th.textContent = header;
                        tableHeaders.appendChild(th);
                      });

                      // Add data rows to the table
                      data.data.data.forEach((rowData, rowIndex) => {
                        const row = document.createElement('tr');

                        rowData.forEach((cellData, cellIndex) => {
                          const cell = document.createElement('td');
                          cell.textContent = cellData;
                          row.appendChild(cell);
                        });

                        tableData.appendChild(row);
                      });
                }
            }
            console.log(data);
    });
}

waitForPywebview(main);