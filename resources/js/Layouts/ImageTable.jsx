import ImageRow from '@/Components/ImageRow';

export default function ImageTable({ header, rows }) {
    return (
        <div className="py-12">
            <div className="max-w-7x1 mx-auto sm:px-6 lg:px-8">
                <div className="overflow-hidden bg-white shadow sm:rounded-lg">
                    <div className="px-4 py-5 sm:px-6">
                        <h3 className="text-lg font-medium leading-6 text-gray-900">Image Information</h3>
                        <p className="mt-1 max-w-2x1 text-sm test-gray-500">View Saved Images Here</p>
                    </div>

                    <div className="border-t border-gray-200">
                        <dl>
                            <div className={"bg-gray-50 px-4 py-2 sm:grid sm:grid-cols-" + header.length + " sm:gap-4 sm:px-6"}>
                                {header.map((element, i) =>
                                    <dt key={i} className="mt-1 text-sm text-gray-900 sm:col-span-1 sm:mt-0 bold">{element}</dt>
                                )}
                            </div>
                        </dl>
                    </div>

                    {rows.map((row, i) =>
                        <ImageRow key={i} row={row} />
                    )}

                </div>
            </div>
        </div>
    );
}