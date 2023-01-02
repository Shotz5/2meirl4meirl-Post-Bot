import React from 'react';

export default function ImageRow({ row }) {
    return (
        <div className="border-t border-gray-200">
            <dl>
                <div className={"bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-" + Object.keys(row).length + " sm:gap-4 sm:px-6"}>

                    {Object.values(row).map((element, i) => 
                        <dd
                            key={i}
                            className="mt-1 text-sm text-gray-900 sm:col-span-1 sm:mt-0"
                            style={{overflowWrap: 'break-word'}}
                        >{element}</dd>
                    )}

                </div>
            </dl>
        </div>
    );
}