import { ScrollView, TouchableWithoutFeedback, Keyboard, View } from 'react-native'
import React from 'react'
import { useSafeAreaInsets } from 'react-native-safe-area-context';


type ScreenLayoutProps = {
    children: React.ReactNode;              // scrollable content
    footer: React.ReactNode;                // sticky footer content
};

// This is a reusable screen layout that has a scrollview in it for content and a sticky part
// for the futtor and buttons. It also handles keyboard dismissal (tapping out of it) and safe area
const ScreenLayout: React.FC<ScreenLayoutProps> = ({ children, footer }) => {
    const insets = useSafeAreaInsets();

    return (
        <TouchableWithoutFeedback onPress={() => Keyboard.dismiss()} accessible={false}>
            <View style={{ flex: 1, backgroundColor: '#fff' }}>

                {/* Area for the scrollable content */}
                <ScrollView
                    style={{flex: 1}}
                    contentContainerStyle={{
                        paddingBottom: 150,
                        paddingTop: insets.top,
                    }}
                    indicatorStyle='black'
                    persistentScrollbar={true}
                    keyboardShouldPersistTaps="handled"     // keyboard dismissal
                
                >
                    {children}
                </ScrollView>
                
                {/* sticky footer area */}
                <View
                    className='w-full bg-white px-6 pt-4 border-t border-gray-300'
                    style={{
                        position: 'absolute',
                        bottom: 0,
                        paddingBottom: insets.bottom === 0 ? 12 : insets.bottom,
                    }}
                >
                    {footer}
                </View>
            </View>


        </TouchableWithoutFeedback>
    )
}

export default ScreenLayout
