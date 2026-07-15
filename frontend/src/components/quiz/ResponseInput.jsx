import { useId } from 'react'



const inputClasses =

  'w-full rounded-md border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 placeholder:text-gray-500 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:bg-gray-100'



/**

 * Answer input for non-multiple-choice Alberta question formats.

 */

function ResponseInput({

  questionType,

  responseFormat = 'numeric',

  value,

  onChange,

  disabled,

  onSubmitAnswer,

  inputRef,

}) {

  const inputId = useId()

  const hintId = useId()



  const handleEnterSubmit = (event) => {

    if (event.key !== 'Enter') return

    // Allow Shift+Enter to insert a newline in written responses only.

    if (questionType === 'written_response' && event.shiftKey) return

    event.preventDefault()

    if (disabled) return

    onSubmitAnswer?.(event)

  }



  if (questionType === 'numerical_response') {

    const isText = responseFormat === 'text'

    return (

      <div className="flex flex-col gap-2">

        <label htmlFor={inputId} className="text-xs font-medium text-gray-700">

          {isText ? 'Your answer' : 'Your answer (number)'}{' '}

          <span className="text-red-700" aria-hidden="true">*</span>

          <span className="sr-only">(required)</span>

        </label>

        <input

          ref={inputRef}

          id={inputId}

          type="text"

          inputMode={isText ? 'text' : 'decimal'}

          enterKeyHint="done"

          autoComplete="off"

          autoCapitalize={isText ? 'off' : undefined}

          spellCheck={isText ? false : undefined}

          required

          placeholder={isText ? 'e.g. mitosis' : 'e.g. 2.5'}

          className={inputClasses}

          value={value}

          aria-describedby={hintId}

          onChange={(event) => onChange(event.target.value)}

          onKeyDown={handleEnterSubmit}

          disabled={disabled}

        />

        <p id={hintId} className="text-xs text-gray-600">

          {isText

            ? 'Short answer — enter the expected term or phrase. Press Enter to submit.'

            : 'Numerical response — enter a single numeric value. Press Enter to submit.'}

        </p>

      </div>

    )

  }



  if (questionType === 'written_response') {

    return (

      <div className="flex flex-col gap-2">

        <label htmlFor={inputId} className="text-xs font-medium text-gray-700">

          Your solution{' '}

          <span className="text-red-700" aria-hidden="true">*</span>

          <span className="sr-only">(required)</span>

        </label>

        <textarea

          ref={inputRef}

          id={inputId}

          rows={6}

          required

          autoComplete="off"

          enterKeyHint="done"

          placeholder="Show your work step by step…"

          className={inputClasses}

          value={value}

          aria-describedby={hintId}

          onChange={(event) => onChange(event.target.value)}

          onKeyDown={handleEnterSubmit}

          disabled={disabled}

        />

        <p id={hintId} className="text-xs text-gray-600">

          Written response — compare your work with the solution guide after

          submitting. Press Enter to submit (Shift+Enter for a new line).

        </p>

      </div>

    )

  }



  return null

}



export default ResponseInput


